# MG_SBY_resample.py

# Short description:
#   A template for the generation of MeqGraft (MG) scripts

# Keywords: ....


# Copyright: The MeqTree Foundation

# Full description:

#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************


#% $Id$ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
# import JEN code for bookmarks
from Timba.Trees import JEN_bookmarks
from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *

import random
Settings.forest_state.cache_policy = 100;

Settings.orphans_are_roots = True;
# from numarray import *
# from string import *
# from copy import deepcopy
import math

# Scripts needed to run a MG_JEN script: 


#-------------------------------------------------------------------------
# Script control record (may be edited here):


#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

# Create Empty LSM - global
lsm=LSM()
solvables = []

def _define_forest (ns):
    global lsm
    global solvables

    # Load a predefined LSM
    lsm.load('spectral.lsm',ns);

    # Get P-Units
    #plist = lsm.queryLSM(cat=1);
    plist = lsm.queryLSM(count=1);

    #for punit in plist:
     #  print 'Gotcha!', punit.name
      # if (punit.type == 0) :
         # Point Source
      #   print 'Point', punit.name, punit.type
       #  sixpack_name = 'sixpack:q='+punit.name
              
       #  I1 = ns.StokesI(q=punit.name) << Meq.Selector(sixpack_name, multi=True,index=[2]);
       #  solvables.append('ISIF[q=J163433+624535]')

    ISIF0 = [23.6,288.0,0.0];
    meq_polclog = meq.polclog(coeff=ISIF0,shape = (1,3));
    meq_polclog.axis_list = record(time=1.0,freq=1400.0e6);
    Isif1 = ns.Isif1 << Meq.Parm(meq_polclog);
    ns.ten << Meq.Constant(10.0);
    I1 = ns.I1 << Meq.Pow(ns.ten,Isif1);
    solvables.append('Isif1');

    meq_polc = meq.polc(coeff=[1.0,0.0],shape=(1,2));
    I2 = ns.I2 << Meq.Parm(meq_polc);
    I3 = ns.I3 << Meq.Multiply(I2,I1);
    solvables.append('I2');

    im_sixpack = ns.r<<Meq.FITSImage(filename="/home/rnijboer/Update/source1a.fits",cutoff=1.0);
    #im_sixpack = ns.r<<Meq.FITSImage(filename="/home/rnijboer/Timba/WH/contrib/RJN/clean.fits",cutoff=1.0);    
    IQUV = ns.IQUV << Meq.Selector(im_sixpack, multi=True,index=[2,3,4,5]);
    I = ns.I << Meq.Selector(IQUV,multi=True,index=[0]);
    #ns.res << Meq.Resampler(ns.I,common_axes=[hiid("TIME"),hiid("FREQ")],mode=1);
    ns.res << Meq.Sum(ns.I, reduction_axes=[hiid("L"),hiid("M")]);

    #ns.res2 << Meq.Resampler(ns.res,common_axes=[hiid("L"),hiid("M")]);
    ns.res2 << Meq.Resampler(ns.res);

    ns.l0 << Meq.Constant(0.0);
    ns.m0 << Meq.Constant(0.0);
    ns.lm << Meq.Composer(ns.l0,ns.m0);
    
    compound = ns.compounder << Meq.Compounder(ns.lm,ns.res2);

    condeq = ns.condeq << Meq.Condeq(ns.compounder,I3);
    #solvables=record(command_by_list=(record(name=['ISIF[q=J163433+624535]'],
    #                         state=record(solvable=True)),
    #                         record(state=record(solvable=False))));
    solver1 = ns.solver1 << Meq.Solver(condeq,solvable=solvables,parm_group=hiid('all'),num_iter=100,epsilon=1.0e-4);


    JEN_bookmarks.create(ns.r, page='Image', viewer='Result Plotter')
    JEN_bookmarks.create(ns.condeq, page='Condeq', viewer='Result Plotter')

#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************






#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

# The function with the standard name _test_forest(), and any function
# with name _tdl_job_xyz(m), will show up under the 'jobs' button in
# the browser, and can be executed from there.  The 'mqs' argument is
# a meqserver proxy object.
# NB: The function _test_forest() is always put at the end of the menu:

def _test_forest (mqs, parent):

 f0 = 1171.0e6
 f1 = 1180.0e6
 t0 = 0.0
 t1 = 43200.0
 nfreq =6
 ntime =1

 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 request = meq.request(cells,rqtype='e1');
 mqs.meq('Node.Execute',record(name='solver1',request=request),wait=True);
 
 

#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_JEN_template.py

if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns)
  print ns.AllNodes()



