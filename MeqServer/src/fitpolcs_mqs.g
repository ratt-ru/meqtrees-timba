### fitpolcs_mqs.g: fitter for polcs using MeqTrees
###
### Copyright (C) 2002
### ASTRON (Netherlands Foundation for Research in Astronomy)
### P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License as published by
### the Free Software Foundation; either version 2 of the License, or
### (at your option) any later version.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###
### $Id$

pragma include once

# These can be uncommented (or set elsewhere prior to include) for debugging
#
#   use_suspend  := T;
#   use_nostart  := T;
#   use_valgrind := T;
   use_valgrind_opts := [ "",
#     "--gdb-attach=yes",          # use either this...
     "--logfile=meqserver",       # ...or this, not both
#     "--gdb-path=/usr/bin/ddd", 
   ""];
   
# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions ) 
{
  print '$Id$';
}

include 'meq/meptools.g'
include 'meq/meqserver.g'

#------ fitpolcs_mqs()
# Fits the given polcs with a new degx x degy polc, computed over the specified 
# domain. Uses the meqserver() for fitting.
# If no domain is specified, then the envelope of the polcs' domains is 
# used. A scale may be specified as [f0,fscale,t0,tscale]. If it is not 
# specified, then a scale corresponding to [0:1] over the domain is used.

const meq.fitpolcs_mqs := function (polcs,degx=0,degy=0,domain=F,scale=F,verbose=1,gui=F)
{
  # polcs must be a vector of polcs; if it's a single polc, then make the vector
  if( is_dmi_type(polcs,'MeqPolc') )
  {
    p := [=];
    p[1] := polcs;
    polcs := p;
  }
  # compute domain of target polc
  if( is_boolean(domain) )
    domain := meq.envelope_domain(polcs);
  if( verbose>0 )
  {
    print 'Merging ',len(polcs),' polcs; destination domain is ',domain;
    for( i in 1:len(polcs) )
      print '  polc ',i,': domain ',polcs[i].domain;
  }
  # create initial new polc
  if( is_boolean(scale) )
    scale := [ domain[1],domain[2]-domain[1],domain[3],domain[4]-domain[3] ];
  newpolc := meq.polc(array(0,degx+1,degy+1),domain=domain,
                    freq0=scale[1],freqsc=scale[2],
                    time0=scale[3],timesc=scale[4]);
  # start meqserver and build a tree
  global mqs;
  mqs := ref default_meqserver(verbose=verbose,gui=gui,debug=[MeqParm=5]);
  # clear the forest -- tough luck if something's there
  # TODO: think about private forests, anonymous nodes, etc.
  mqs.meq('Clear.Forest');
  
  print mqs.createnode(meq.parm('fitpolc_p1',polc=polcs));
  print mqs.createnode(meq.parm('fitpolc_p2',polc=newpolc,groups='Parm'));
  print mqs.createnode(meq.node('MeqCondeq','fitpolc_eq',children="fitpolc_p1 fitpolc_p2"));
  
  rec := meq.node('MeqSolver','fitpolc_solver',children="fitpolc_eq");
  rec.default := [ num_iter = 3 ];
  rec.parm_group := hiid('Parm');
  rec.solvable := meq.solvable_list("fitpolc_p2");
  print mqs.createnode(rec);
  
  # resolve children
  mqs.resolve('fitpolc_solver');
  
  if( verbose>1 )
  {
    for( nm in "fitpolc_p1 fitpolc_p2 fitpolc_eq" )
      print mqs.meq('Node.Publish.Results',[name=nm]);
  }
  
  # perform a fit. 
  global cells,request,res;
  # figure out an appropriate cells first
  cells := meq.cells(domain,num_freq=max(2*degx,3),num_time=max(2*degy,3));
#  print cells;
  request := meq.request(cells,calc_deriv=2);
#  print request;
  res := mqs.meq('Node.Execute',[name='fitpolc_solver',request=request],T);
#  print res;
  
  if( has_field(res.result.vellsets[1],'fail') )
  {
    fl := res.result.vellsets[1]['fail'];
    print 'Solve failed: ',fl;
    fail fl[1].message;
  }
  
  # return the new polc
  return mqs.getnodestate('fitpolc_p2').polcs;
}

# test for fitpolcs_mqs()
const meq_test.fitpolcs_mqs := function ()
{
  global polcs,polc;
  polcs := [=];
  polcs[1] := meq.polc(array([0,1],2,1),domain=meq.domain(0,1,0,1));
  polcs[2] := meq.polc(array([2,-1],2,1),domain=meq.domain(1,2,0,1));
  polcs[3] := meq.polc(array([-2,1],2,1),domain=meq.domain(2,3,0,1));
  polc := meq.fitpolcs_mqs(polcs,degx=4,degy=1,scale=[0,1,0,1],verbose=1);
  print polc;
}



