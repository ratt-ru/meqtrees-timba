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

script_name = 'MG_RJN_simul.py'

# Short description:
#   Predict simulated data from a LSM and write it to a (existing) MS.

# Keywords: LSM, simulations


# History:
# - 12 Sep 2005: creation
# - 26 Oct 2005: adaptation from /SBY/MG_LSM_test.py
# - 07 Mar 2006: adaptation from MG_RJN_load_lsm.py

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

from Timba.Contrib.RJN import spigot2sink
from Timba.Contrib.RJN import RJN_sixpack_343
from Timba.Contrib.JEN import MG_JEN_forest_state

# to force caching put 100
Settings.forest_state.cache_policy = 1


# Create Empty LSM - global
lsm=LSM()

#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
    global lsm

    # Load a predefined LSM
    lsm.load('343_points.lsm',ns);

    # Get all Cat. 1 P-Units
    #plist = lsm.queryLSM(cat=1);
    plist = lsm.queryLSM(count=2);

    print lsm.getPUnits()
    print len(plist)

    # Phase center of the observation
    RA_0 = 4.35664870004;
    Dec_0 = 1.09220644132;
    pc_name = 'Phase Center';
    RA_root = RJN_sixpack_343.make_RA(pc_name,RA_0,ns);
    Dec_root = RJN_sixpack_343.make_Dec(pc_name,Dec_0,ns);
    ns.radec0(pc_name) << Meq.Composer(RA_root,Dec_root);

    stations = range(0,14);
    ifrs = TDL_Cohset.stations2ifrs(stations);
    rr = MG_JEN_forest_state.MS_interface_nodes(ns,ra0=RA_0,dec0=Dec_0);

    

    
    print "****************",ifrs;
    for ifr in ifrs:
        child_list = [];
        for punit in plist:
           print 'Gotcha!', punit.name
           if (punit.type == 0) :
              # Point Source
              print 'Point', punit.name, punit.type
              sixpack_name = 'sixpack:q='+punit.name
              
              # LMN
              ra = punit.sp.getRA();
              dec = punit.sp.getDec();
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

              print punit.getSP().root().name;

              # LMN
              ra = punit.sp.getRA();
              dec = punit.sp.getDec();
              radec1 = ns.radec1(q=punit.name) << Meq.Composer(ra,dec);
              lmn = ns.lmn(q=punit.name) << Meq.LMN(radec_0=ns.radec0(pc_name), radec=radec1);
              n = ns.n(q=punit.name) << Meq.Selector(lmn,index=2);
              lmn1 = ns.lmn_minus1(q=punit.name) << Meq.Paster(lmn,n-1, index=2);
              sqrtn = ns << Meq.Sqrt(n);
              
              # Construct UVInterpol tree
              IQUV = ns.IQUV(q=punit.name) << Meq.Selector(sixpack_name, multi=True,index=[2,3,4,5]);
              Corr = ns.corr(q=punit.name) << Meq.Stokes(IQUV);
              fft = ns.fft(q=punit.name) << Meq.FFTBrick(Corr);

              # KJones of the Phase Center
              skey1 = TDL_radio_conventions.station_key(ifr[0]);
              skey2 = TDL_radio_conventions.station_key(ifr[1]);
              uvw1 = rr.uvw[skey1];
              uvw2 = rr.uvw[skey2];
              uvw = ns.uvw(s1=skey1,s2=skey2) << Meq.Subtract(uvw1, uvw2);
              KJones = ns.KJones(s1=skey1,s2=skey2,q=punit.name) << \
                                 Meq.VisPhaseShift(lmn=lmn1, uvw=uvw)/ n;

              # Transformed uvw coordinates 
              l = ns.l(q=punit.name)<<Meq.Selector(lmn,index=0);
              m = ns.m(q=punit.name)<<Meq.Selector(lmn,index=1);
              u = ns.u(s1=skey1,s2=skey2)<<Meq.Selector(uvw,index=0);             
              v = ns.v(s1=skey1,s2=skey2)<<Meq.Selector(uvw,index=1);         
              w = ns.w(s1=skey1,s2=skey2)<<Meq.Selector(uvw,index=2);     

              uvwp = ns.uvwp(s1=skey1,s2=skey2)<<Meq.Composer(u-w*l/n,v-w*m/n,w);          

              # Interpolation
              interpol = ns.interpol(s1=skey1,s2=skey2,q=punit.name) << \
                   Meq.UVInterpol(Method=1,children=[fft,uvwp],additional_info=True);

              patch_predict = ns.patch(s1=skey1,s2=skey2,q=punit.name) << \
                   Meq.Multiply(KJones,interpol);

              child_list.append(patch_predict);

           pass # for if / else

        pass # for punit
       
        skey1 = TDL_radio_conventions.station_key(ifr[0]);
        skey2 = TDL_radio_conventions.station_key(ifr[1]);
        print "creating predict",skey1,skey2
        predict_root = ns.predict(s1=skey1,s2=skey2)<<Meq.Add(children=child_list);
        ns.sink(s1=skey1,s2=skey2) << Meq.Sink(predict_root,station_1_index=int(skey1),station_2_index=int(skey2));
           
    pass # for ifr

    



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
 
 msname    = '343test.MS'
 inputrec  = spigot2sink.create_inputrec(msname, tile_size=10)
 outputrec = spigot2sink.create_outputrec()
 req = meq.request();
 req.input = record(ms=inputrec);
 req.output = record(ms=outputrec);

 mqs.execute('VisDataMux',req,wait=False);

 

 

def _tdl_job_show_lsm(mqs, parent):
  global lsm
  lsm.setMQS(mqs)
  lsm.display()

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




