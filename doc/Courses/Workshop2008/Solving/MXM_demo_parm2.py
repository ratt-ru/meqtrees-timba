# MXM_demo_parm2.py:

# Simple Tree with a solver and several  parameters, demonstrates parameter options 

 
#********************************************************************************
# Initialisation:
#********************************************************************************

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

from Timba.TDL import *
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""
   # You can attach a meptable to a Parm by setting the field table_name,
   # the funklet will then be initialized (if available) from 
   # and (after solving) stored in the table.
   meptable ="test2.mep"
   #set this as the table for all our parms

   
   #tiling means that you have independent solutions for different time/freq slots.
   #We make our simple_parm less simple, by tiling it in freq and time:

   
   simple_parm = ns['simple_parm'] << Meq.Parm(1.,node_groups='Parm',table_name=meptable,
                                               tiling= record(freq=1,time=2)
                                               #Gives an independent solution per freq. cell
                                               # and per 2 time cells
                                               )

   
   # A more general, but sometimes slow, option is to make use of the Aips++ functional interpreter
   # to create any real function. This is done by setting the "function" field of the polc.
   # use x0,...,xn for axes (time,freq etc.)
   # use p0,...,pn for your solvable coeffiecients
   functional = meq.polc([1.,2.,1.5]); # The number of coeffs should match the number of p# in function 
   functional.function = "p0+p1*exp(-0.01*x0^2)*sin(x1*p2)";
   functional_parm =  ns['functional_parm'] <<Meq.Parm(init_funklet = functional ,node_groups='Parm',table_name=meptable);





 
   # Now lets fit simple_parm to the functional_parm
   # see how the number of solvables is increased in the solver plot. This is because our simple_parm is actually
   # a collection of 10*5 (on the 10 freq/10 time domain defined in test_forest) independent funklets.
   condeq_simple_functional = ns['condeq_simple_functional'] << Meq.Condeq(children=(simple_parm,functional_parm))

   solver = ns['solver'] << Meq.Solver(children=condeq_simple_functional,
                                       solvable = ['simple_parm'], #list of solvable parameters 
                                       num_iter = 10,        #stop after 10 iterations or after convergence
                                       epsilon = 1e-4,       #convergence limit, good default
                                       last_update=True,     #sends last update to parms after convergence
                                       save_funklets=True    #needed to save funklets in parmtable
                                       )


   # When running the script, first display the bookmarks, since some of the nodes wont have a result cached after the run
   bm = record(name='result',page=
               [record(viewer='Result Plotter',udi='/node/simple_parm', publish=True, pos=(0,0)),
                record(viewer='Result Plotter',udi='/node/functional_parm', publish=True, pos=(0,1)),
                record(viewer='Result Plotter',udi='/node/condeq_simple_functional', publish=True, pos=(1,0)),
                record(viewer='Result Plotter',udi='/node/solver', publish=True, pos=(1,1))
                ])
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(0,10,0,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=10)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='solver', request=request))
    return result
       
#********************************************************************************
#********************************************************************************

# You can also view the solutions of your parm on different domains by executing them again.
# It will select the funklets in the meptable on name and domain. 

def _tdl_job_plot_parm (mqs, parent):
    """Executes our solvable parm  on the full domain. It gets its values from the meptable"""
    # Since the initialization of the parm is different for solvable and non-solvable parms, we make sure
    # that the state of the parm is set to solvable=False;
    
    mqs.meq('Node.Set.State',record(name='simple_parm',state=record(solvable = False)));
    domain = meq.domain(0,10,0,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=10)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='simple_parm', request=request))
    return result


def _tdl_job_plot_parm_on_partial_domain (mqs, parent):
    """Executes our solvable parm  on part of the full domain. It gets its values from the meptable"""
    mqs.meq('Node.Set.State',record(name='simple_parm',state=record(solvable = False)));
    domain = meq.domain(1,5,3,7)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=5, num_time=4)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='simple_parm', request=request))
    return result

# You can use the ignore_time flag of the parm to ignore the time component of the domain when searching in the meptable.
# This is especially useful if you have parameters of a calibration run that you want to apply to a measurement taken at a different time

def _tdl_job_test_calibration_parm (mqs, parent):
   """Executes our solvable parm on a domain for which we do not have time solutiosn. It gets its values from the meptable.
   The ignore_time flag makes sure the parm is initialized from the table anyway."""
   mqs.meq('Node.Set.State',record(name='simple_parm',state=record(solvable = False,ignore_time=True)));

   #change the time domain
   domain = meq.domain(0,10,30,40)                            # time is changed to a range for which we dont have values in the meptable
   cells = meq.cells(domain, num_freq=10, num_time=10)
   request = meq.request(cells, rqtype='ev')
   result = mqs.meq('Node.Execute',record(name='simple_parm', request=request),wait=True)
   #
   #reset to default
   #
   mqs.meq('Node.Set.State',record(name='simple_parm',state=record(ignore_time=False)));
   return result


       
#********************************************************************************
#********************************************************************************



