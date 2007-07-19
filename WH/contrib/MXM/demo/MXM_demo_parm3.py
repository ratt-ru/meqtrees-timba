# MXM_demo_parm3.py:

# A  model for a Gaussian beamshape

 
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
from Timba.Meq import meqds

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []


def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""
   # You can attach a meptable to a Parm by setting the field table_name,
   # the funklet will then be initialized (if available) from 
   # and (after solving) stored in the table.
   meptable ="test3.mep"
   #set this as the table for all our parms

   
   # Here we create a simple beamshape model. This is a function that not only depends on freq and time, but also on L,M
   # We use a MeqCompounder to create the L,M coordinates in the request

   # The function of a functional can become very complex, we cut the string in pieces to keep an overview
   # The beam we use is a Gaussian
   # beam = A * exp ( (-(L-L_offset)^2 - (M-M_offset)^2) * 25 * freq /3.e8 )
   # With A, L_offset, M_offset functions of time 
   # x0=time, x1=freq, x2=l, x3 = m
   A = "p0 + p1*x0 + p2*x0*x0";
   A_coeff = [1.,0.01,0.01];
   L_off = "p3 +p4*x0 +p5 *x0*x0" # keep track of your p# numbering!
   L_coeff = [0.,0.001,-0.001];
   L_Term = "-1*(x2-"+L_off+")^2";

   M_off = "p6 +p7*x0 +p8 *x0*x0"
   M_coeff = [0.,-0.002,-0.002];
   M_Term = "-1*(x3-"+M_off+")^2";

   exp = "exp( ("+L_Term+M_Term+") * 25. * x1 /3e8)";
   beam_function = "("+A +") * "+exp ; 

   coeff =[];
   coeff+=A_coeff;
   coeff+=L_coeff;
   coeff+=M_coeff;
   
   functional = meq.polc(coeff); # The number of coeffs should match the number of p# in function 
   functional.function = beam_function;


   
   beam =  ns['beam'] <<Meq.Parm(init_funklet = functional ,node_groups='Parm',table_name=meptable);




   # L,M coordinates
   l=[0.1, 0.001]
   m=[0.2, 0.002]
   ns.l0<< Meq.Parm(l,node_groups='Parm')
   ns.m0<< Meq.Parm(m,node_groups='Parm')
   
   # this will generate the LM grid
   ns.lm<<Meq.Composer(ns.l0, ns.m0)
   
   # the compounder combines a time/freq request with the l,m values of its first child
   # the resulting request is sent to the second child
   compounder = ns.compounder<<Meq.Compounder(children=[ns.lm,ns.beam],common_axes=[hiid('l'),hiid('m')])
   
   
   # Make a bookmark of the result nodes, for easy viewing:
   # When running the script, first display the bookmarks, since some of the nodes wont have a result cached after the run
   bm = record(name='result',page=
               [record(viewer='Result Plotter',udi='/node/compounder', publish=True, pos=(0,0)),
                record(viewer='Result Plotter',udi='/node/beam', publish=True, pos=(1,0))
                ])
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True



      
#********************************************************************************
#********************************************************************************
def _tdl_job_execute(mqs,parent,write=True):
   """Execute the compounder, at the moment the display of the l,m axis doesnt work properly,
   use display beam to see the beam"""
   domain = meq.domain(1408000000., 1408001000.,1,10)  # (f1,f2,t1,t2)
   cells = meq.cells(domain, num_freq=10, num_time=11)
   request = meq.request(cells, rqtype='ev')
   result = mqs.meq('Node.Execute',record(name='compounder', request=request))
   return result

# to view the beam you need to make a request that contains also l,m
# this is done in the function below
def _tdl_job_display_beam(mqs,parent,write=True):
    freq_range = [1408000000., 1408001000.];
    time_range = [0.,1.];
    lm_range = [-0.01,0.01];
    request  = make_request(Ndim=4,dom_range=[freq_range,time_range,lm_range,lm_range],nr_cells=[5,5,20,20]);
    a = mqs.meq('Node.Execute',record(name='beam',request=request),wait=True);









def make_request(Ndim=4,dom_range=[0.,1.],nr_cells=5):

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
    
    # workaround to get domain with more axes running 

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
#********************************************************************************
#********************************************************************************

## The Gaussian beam is defined as a parm, so you could solve for its coeffiecients
## You could try this by extending the tree with a condeq and a solver and of course
## some tree to fit the beam on. 




    
