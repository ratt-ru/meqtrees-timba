#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

script_name = 'MG_MXM_functional.py'
last_changed = '29sep2005'

# Short description:
#   Demo and helper functions for the compiled funklet


# Copyright: The MeqTree Foundation 

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
from numarray import *

from Timba.Contrib.MXM.TDL_Functional import *
from Timba.Contrib.MXM.TDL_Funklet import *



# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

# Make sure our solver root node is not cleaned up
Settings.orphans_are_roots = True;

def _define_forest1 (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  _add_axes_to_forest_state();
  par=[];
  coeff=[];
  for i in range(6):
      coeff.append([1.]) #set c00 coeff to 1. instead of default 0.
      par.append(_polc2d(startp=i*4,shape=[2,2],x0="x0",x1="x1",coeff = coeff[i]));
  gaussian = _gaussian2d(par,'(x2-1.)','(x3-1.)');
  print "function :",gaussian;

# set cross-term (= 4th term)  to 0
  coeff[3]=[0.,0.,0.,0.];

  polc = meq.polc(coeff=coeff,subclass=meq._funklet_type)
# set the function field, if this is defined, the funklet will always evaluated via this string
  polc.function = gaussian;

#some variation on coeff for nonsolvable
  coeff[0][2]=0.001;
#make cross-term (= 4th term) time-freq dependent
  coeff[3]=[0.,1.,0.5,0.]
  polc2= meq.polc(coeff=coeff,subclass=meq._funklet_type)
  polc2.function = gaussian;

  ns['solver'] << Meq.Solver(
      num_iter=5,debug_level=10,solvable="x",last_update=True,save_funklets=True,
      children = Meq.Condeq(
        ns.y<<Meq.Parm(polc2,node_groups='Parm'),
        (0 + (ns.x << Meq.Parm(node_groups='Parm',table_name='test_compiled',save_all=True)))
      ),
    );

  ns.dummy<<Meq.Parm([[0,1],[1,0]],node_groups='Parm');



def _define_forest2(ns):
  """example function to show how to use the  Functional class"""
  _add_axes_to_forest_state();
  

  f1=Functional("p0+p1*x0",pp=dict(p1=1.),Npar=2);
  
  print "f1",f1.getFunklet();
  
  f2=Functional("p0+p1*x1",pp=dict(p1=1.),Npar=2);
  print "f2",f2.getFunklet();

  

  f3=create_polc(shape=[3,2]);
  print "f3",f3.getFunklet();
  f3.display();

  f4=Functional(function = "sin(p0)+p1+p2*x2*x3",pp=dict(p0=f1,p1=f2,p2=f3),test=dict(x0=1,x1=2,x2=2,x3=5)); #replaces p0 by f1,p1 by f2...etc..
  #if the pp argument contains number this will be the init_value of te coefficient,
  #therefore, for the moment the only allowed keys in the dictionary are p0...pN
  #test contains x values for test evaluation

  polc=f4.getFunklet();

  print "created funklet",polc;

  print"eval:",f4.eval();

  f4.display(var_def={'x0':"time",'x1':"freq",'p0':"TheFirstParameter"});
  
  dom = meq.domain(0,1,0,2);
  cells = meq.cells(dom,num_time=10,num_freq=5);

  f4.setCoeff(0,2.);
  f4.setCoeff(1,3.);
  f4.setCoeff(2,4.);
  result = f4.plot(cells=cells);



  ns['solver'] << Meq.Solver(
      num_iter=5,debug_level=10,solvable="x",
      children = Meq.Condeq(
        ns.y<<Meq.Parm([[1,2,3]],node_groups='Parm'),
        (0 + (ns.x << Meq.Parm(polc,node_groups='Parm')))
      ),
    );

  ns.dummy<<Meq.Parm([[0,1],[1,0]],node_groups='Parm');
  #ftest = Funklet(record(function="67."));
  #print "ftest",ftest;
  #print ftest.eval();


def _define_forest(ns):
  _define_forest2(ns);


def _test_forest (mqs,parent):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  # run tests on the forest 
  # run dummy first, to make python know about the extra axes (some magic)
  _dummy(mqs,parent);
  

  request = _make_request(nr_cells=[5,5,10,10]);
  print request;
  a = mqs.meq('Node.Execute',record(name='solver',request=request),wait=True);

def _dummy(mqs,parent):
  # run tests on the forest 
  dom = meq.domain(0,1,0,1);
  cells = meq.cells(dom,num_freq=2,num_time=2);
  request = meq.request(cells);
  a = mqs.meq('Node.Execute',record(name='dummy',request=request),wait=True);


#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================


def _add_axes_to_forest_state(axes=['l','m'], start=2):
  """define extra axes in forest state"""
  forest_state=meqds.get_forest_state();
  axis_map=forest_state.axis_map;
  for i in range(len(axes)):
    axis_map[i+start].id=hiid(axes[i]);
  Settings.forest_state.axis_map = axis_map;

def _make_request(Ndim=4,dom_range=[0.,1.],nr_cells=5):
  """make multidimensional request, dom_range should have length 2 or be a list of
  ranges with length Ndim, nr_cells should be scalar or list of scalars with length Ndim"""
  forest_state=meqds.get_forest_state();
  axis_map=forest_state.axis_map;

  range0 = [];
  if is_scalar(dom_range[0]):
    for i in range(Ndim):		
      range0.append(dom_range);
  else:
    range0=dom_range;
  nr_c=[];
  if is_scalar(nr_cells):
    for i in range(Ndim):		
      nr_c.append(nr_cells);
  else:
    nr_c =nr_cells;
  dom = meq.domain(range0[0][0],range0[0][1],range0[1][0],range0[1][1]);
  cells = meq.cells(dom,num_time=nr_c[0],num_freq=nr_c[1]);

  #workaround to get domain with more axes running 

  for dim in range(2,Ndim):
    id = axis_map[dim].id;
    if id:
      dom[id] = [float(range0[dim][0]),float(range0[dim][1])];
      step_size=float(range0[dim][1]-range0[dim][0])/nr_c[dim];
      startgrid=0.5*step_size+range0[dim][0];
      grid = [];
      cell_size=[];
      for i in range(nr_c[dim]):
        grid.append(i*step_size+startgrid);
        cell_size.append(step_size);
      cells.cell_size[id]=array(cell_size);
      cells.grid[id]=array(grid);
      cells.segments[id]=record(start_index=0,end_index=nr_c[dim]-1);

  cells.domain=dom;
  request = meq.request(cells);
  return request;

def _polc2d(startp=0,shape=[1,1],x0="x0",x1="x1",coeff=[]):
  """returns the string for a two-dimensional polc with shape = shape:
  p0+p1x0+p2x0^2+p3x1+p4x0x1+p5x1x0^2+...
  parameter counting starts from startp,
  per default the coefficients are 0"""
  func=""
  if len(shape)==1: 
    shape.append(1);
  if shape[0]==0:
    shape[0]=1;
  if shape[1]==0:
    shape[1]=1;
  nr_par=0; 
  for i in range(shape[1]):
    for j in range(shape[0]):
      nr_par=nr_par+1;
      if(len(coeff)<nr_par):
        coeff.append(0.);
      func=func+'p'+str(startp);
      for i2 in range(j):
        func = func + '*'+ x0;
      for i1 in range(i):
        func = func + '*'+ x1;
      func = func + "+"
      startp=startp+1;
  #remove last +
  
  return func[0:len(func)-1];  

  
def _gaussian2d(par_list=["p0","p1","p2","p3","p4","p5"],axis0="x0",axis1="x1"):
  """returns string of 2d gaussian : exp(-(p0 + p1x0 + p2x1 + p3x0x1 + p4x0^2 + p5x1^2))
  par_list must have length 6"""
  if len(par_list) < 6:
    print "not enough parameters defined"
    return;
  x=['','*'+axis0,'*'+axis1,'*'+axis0+'*'+axis1,'*'+axis0+'^2','*'+axis1+'^2']
  func = 'exp(-1*('
  for i in range(6):
    func=func+"("+par_list[i]+")"+x[i];
    if(i<5):
      func = func + '+';
  func=func+"))";
  return func;
    
# this is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
