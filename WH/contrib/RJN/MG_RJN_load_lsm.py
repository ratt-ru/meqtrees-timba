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

script_name = 'MG_RJN_load_lsm.py'

# Short description:
#   First try at generating a LSM and connecting Point and Patch P-Units

# Keywords: LSM


# History:
# - 12 Sep 2005: creation
# - 26 Oct 2005: adaptation from /SBY/MG_LSM_test.py

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from random import *

from Timba import utils
_dbg = utils.verbosity(0, name='LSM_load')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed


from Timba.TDL import *
from Timba.TDL import Settings
from Timba.Meq import meq
from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *

from Timba.Trees import TDL_Cohset
from Timba.Trees import TDL_radio_conventions

from Timba.Contrib.RJN import RJN_sixpack_343
from Timba.Contrib.JEN import MG_JEN_forest_state

# to force caching put 100
Settings.forest_state.cache_policy = 100


# Create Empty LSM - global
lsm=LSM()
#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
    global lsm

    # Load a predefined LSM
    lsm.load('3c343_b.lsm',ns);

    # Get all Cat. 1 P-Units
    plist = lsm.queryLSM(cat=1);

    print lsm.getPUnits()
    print len(plist)

    stations = range(2);
    ifrs = TDL_Cohset.stations2ifrs(stations);
    rr = MG_JEN_forest_state.MS_interface_nodes(ns);

    # Phase center of the observation
    RA_0 = 4.35664870004;
    Dec_0 = 1.09220644132;
    pc_name = 'Phase Center';
    RA_root = RJN_sixpack_343.make_RA(pc_name,RA_0,ns);
    Dec_root = RJN_sixpack_343.make_Dec(pc_name,Dec_0,ns);
    ns.radec0(pc_name) << Meq.Composer(RA_root,Dec_root);

    child_list = [];

    for ifr in ifrs:
        for punit in plist:
           print 'Gotcha!', punit.name
           if (punit.type == 0) :
              # Point Source
              print 'Point', punit.name, punit.type
              sixpack_name = 'sixpack:q='+punit.name
              
              # LMN
              ra = punit.sp.getRA;
              dec = punit.sp.getDec;
              radec = ns.radec(q=punit.name) << Meq.Composer(ra,dec);
              lmn = ns.lmn(q=punit.name) << Meq.LMN(radec_0=ns.radec0(pc_name), radec=radec);
              n = ns.n(q=punit.name) << Meq.Selector(lmn,index=2);
              lmn1 = ns.lmn_minus1(q=punit.name) << Meq.Paster(lmn,n-1, index=2);
              sqrtn = ns << Meq.Sqrt(n);

              # Construct Point like predict
              ns.StokesI(q=punit.name) << Meq.Selector(sixpack_name, multi=True,index=[2]);
              ns.StokesQ(q=punit.name) << Meq.Selector(sixpack_name, multi=True,index=[3]);
              ns.StokesU(q=punit.name) << Meq.Selector(sixpack_name, multi=True,index=[4]);
              ns.StokesV(q=punit.name) << Meq.Selector(sixpack_name, multi=True,index=[5]);
              
              XX = ns.xx(q=punit.name) << (ns.StokesI(q=punit.name)+ns.StokesQ(q=punit.name))*0.5;
              YX = ns.yx(q=punit.name) << Meq.ToComplex (ns.StokesU(q=punit.name),
                                                                                                        ns.StokesV(q=punit.name))*0.5;
              XY = ns.xy(q=punit.name) << Meq.Conj(YX);
              YY = ns.yy(q=punit.name) << (ns.StokesI(q=punit.name)-ns.StokesQ(q=punit.name))*0.5;
              corr = ns.Corr(q=punit.name)<<Meq.Composer(XX,XY,YX,YY);

              # KJones
              skey1 = TDL_radio_conventions.station_key(ifr[0]);
              KJones1 = ns.KJones(s=skey1,q=punit.name) << Meq.VisPhaseShift(lmn=lmn1, 
                                           uvw=ns[rr.uvw[skey1]])/sqrtn;
              skey2 = TDL_radio_conventions.station_key(ifr[1]);
              KJones2a = ns.KJones(s=skey2,q=punit.name) << Meq.VisPhaseShift(lmn=lmn1, 
                                           uvw=ns[rr.uvw[skey2]])/sqrtn;
              KJones2 = ns.Kconj(s=skey2,q=punit.name)<<Meq.Conj(KJones2a);
              dft = ns.DFT(s1=skey1,s2=skey2,q=punit.name)<<Meq.Multiply(corr,KJones1,KJones2);

              child_list.append(dft)

           else:
              # Patch Source
              print 'Patch', punit.name, punit.type
              sixpack_name = 'sixpack:q='+punit.name
              

              # Construct UVInterpol tree

              #child_list.append(sixpack_name)

           pass # for punit
        pass # for ifr

    predict_root = ns['predict']<<Meq.Add(children=child_list);

########################################################################





#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================





#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
 global lsm
 #display LSM within MeqBrowser
 #l.display()
 # set the MQS proxy of LSM
 #lsm.setMQS(mqs)

 

 f0 = 1200e6
 f1 = 1600e6
 t0 = 0.0
 t1 = 3600.0
 nfreq = 10
 ntime = 10
 # create cells
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 # set the cells to LSM
 #lsm.setCells(cells)
 # query the MeqTrees using these cells
 #lsm.updateCells()
 # display results
 #lsm.display()

 request = meq.request(cells=cells, eval_mode=0);
 args = record(name='predict', request=request);
 mqs.meq('Node.Execute', args, wait=False);

##############################################################
#### test routine to query the LSM and get some Sixpacks from   
#### PUnits
def _tdl_job_query_punits(mqs, parent):
 global lsm
 # obtain the punit list of the 3 brightest ones
 plist=lsm.queryLSM(count=3)
 for pu in plist:
  my_sp=pu.getSP()
  my_sp.display()

#####################################################################
#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
  print '\n*******************\n** Local test of:',script_name,':\n'
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  #display LSM without MeqBrowser
  # create cell
  freqtime_domain = meq.domain(10,1000,0,1);
  cells =meq.cells(domain=freqtime_domain, num_freq=2,  num_time=3);
  lsm.setCells(cells)
  lsm.display(app='create')
#********************************************************************************
#********************************************************************************




