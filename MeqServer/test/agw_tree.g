############## glish script to make a simple MeqTree ################
##############   as described in 'meqs for dummies'  ################
if( any(argv == '-runtest' ) ) {
  root_path := './'
  meq_path  := './'
  app_path  := './'
} else {
  root_path := ''
  meq_path  := 'meq/'
  app_path  := 'appagent/'
}

default_debuglevels := [  MeqNode       =2,
                          MeqForest     =2,
                          MeqSink       =2,
                          MeqSpigot     =2,
                          MeqVisHandler =2,
                          MeqServer     =2,
                          meqserver     =1 ];
                          
include spaste(app_path,'/app_defaults.g')
include spaste(root_path,'dmitypes.g')
include spaste(root_path,'octopussy.g')
include spaste(app_path,'/app_proxy.g')
include spaste(meq_path,'/meqserver.g')
include spaste(meq_path,'/meptable.g')
                      
# inits a meqserver
const mqsinit := function (verbose=default_verbosity,debug=[=],gui=use_gui)
{
  global mqs;
  if( !is_record(mqs) )
  {
    mqs := meq.server(verbose=verbose,options="-d0 -meq:M:O:MeqServer",gui=gui);
# the -nogw option seems to prevent server startup, so browser cannot see the result
#   mqs := meq.server(verbose=verbose,options="-d0 -nogw -meq:M:O:MeqServer",gui=gui);

    if( is_fail(mqs) )
      fail;
    mqs.init([output_col="PREDICT"],wait=T);
    if( !( is_boolean(debug) && !debug ) )
    {
      for( lev in field_names(default_debuglevels) )
        mqs.setdebug(lev,default_debuglevels[lev]);
      if( is_record(debug) )
        for( lev in field_names(debug) )
          mqs.setdebug(lev,debug[lev]);
    }
  }
}

global mqs;

#### 1
# instantiate a 'Meq' server called 'mqs' by calling the mqsinit function
# the server does the work of creating nodes etc
mqsinit(debug=debug,verbose=verbose,gui=gui)

# now create a simple MeqTree

#### 2
# first create 2x2 polc
# The 'polc' array will be used to store the coefficients a,b,c,d
# for the polynomial fit in x and y (a +bx +cy +dxy) that we will do below
polc_array := array(as_double(0),2,2) 
polc_array[1,1] := as_double(1)
# initially we have guessed the coefficients a=1, and b,c,d = 0

#### 3
# we now create a time-frequency 'domain' with range 0 to 2 in frequency and
# 0 to 1 in time 
test_domain := meq.domain(0,2,0,1);

#### 4
# create an actual MeqPolc from the polc_array and the domain specification
meq_polc := meq.polc(polc_array,domain=test_domain)
                                                                                
#### 5
# we now create a leaf called 'coeff' which is of type MeqParm and contains
# the MeqPolc we created previously. It has no children
mqs.meq('Create.Node',meq.parm('coeff',meq_polc,groups='Parm'));

#### 6
# now create a leaf MeqFreq node called 'freq' which has no children
mqs.meq('Create.Node',meq.node('MeqFreq','freq'));

#### 7
# create a leaf MeqTime node called 'time' which has no children
mqs.meq('Create.Node',meq.node('MeqTime','time'));

#### 8
# create a MeqAdd node called 'add' which has the children 'freq' and
# 'time'. As its name indicates it will add the contents of 'freq' and
# 'time' together.
mqs.meq('Create.Node',meq.node('MeqAdd','add',children="freq time"));

#### 9
# create a MeqCondeq node called 'condeq'. A MeqCondeq compares the 
# contents of the 'add' and 'coeff' nodes 
mqs.meq('Create.Node',meq.node('MeqCondeq','condeq',children="add coeff"));

#### 10
# now define parameters for the solver - there are several parameters
rec := meq.node('MeqSolver','solver',children="condeq");
# specify that we are to iterate the solution 3 times
rec.default := [ num_iter = 3 ];
rec.parm_group := hiid('Parm');
# tell it that we are solving for parameters contained within the "coeff" node
rec.solvable := meq.solvable_list("coeff");

#### 11
# now create a node that is a MeqSolver using the glish 'rec' structure
# that we have just defined
mqs.meq('Create.Node',rec);

#### 12
# resolve children - here the solver is the starting node for
# locating the positions of child nodes in the repository. Each
# node downstream of the starting node will also find its children.
mqs.resolve('solver');

#### 13
# Now split the domain into a 8 x 4 "cells' array in time and
# frequency. The frequency range will be split into 8 increments, 
# while the time range will be split into 4 increments
# time
cells := meq.cells(test_domain,num_freq=8,num_time=4);

#### 14
# now create a calculation request for the 'cells' object - we just want 
# to calculate first order derivatives
request := meq.request(cells,rqid=meq.rqid(),calc_deriv=1);

#### 15
# finally tell the solver to execute the request
res := mqs.meq('Node.Execute',[name='solver',request=request],T);

############### end of glish script to make a simple MeqTree ####################
