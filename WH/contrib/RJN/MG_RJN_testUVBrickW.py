#!/usr/bin/python

########
## This script needs to be run in the MeqBrowser,

# The script compares resut from the FFTBrick / UVInterpolateWave
#    with that of the DFT node.
# There is a solver node that solves for the source position in the DFT node
# The CondEq node compares the Result form the UVInterpolateWave and the DFT nodes

# In the define_forest function the Tree is defined,
#   including the position of the (only) source
#   and the baseline under consideration.
# In the test_forest function the Frequency / Time domain is defined

# Get the Sixpack definition from RJN. 

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

from Timba.Contrib.RJN import RJN_sixpack

# Get some Python modules
import re
import math
import random

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

# Define Bookmarks
Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/corr",viewer="Result Plotter",pos=(0,0)),
      record(udi="/node/interpol",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/fft",viewer="Result Plotter",pos=(1,0)),
      record(udi="/node/image",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/Condeq",viewer="Result Plotter",pos=(2,0)),
      record(udi="/node/pspredict",viewer="Result Plotter",pos=(2,1))])]);
# to force caching put 100
Settings.forest_state.cache_policy = 100


########################################################
def _define_forest(ns): 
    
 # Construction of a Phase Center Two-Pack (RA, DEC)
 # RA and Dec coordinates of the Patch Phase Center
 RA_0 = 4.35664870004
 Dec_0 = 1.09220644132
 ra0 = ns.ra0 << RA_0;
 dec0 = ns.dec0 << Dec_0;
 radec0 = ns.radec0 << Meq.Composer(ra0,dec0);
 # Initialize the name list for the PatchComposer node
 child_rec = [radec0];

 # Construction of a single baseline
 # Reference position
 X0 = 0.0;
 Y0 = 0.0;
 Z0 = 0.0;
 x0 = ns.x0 << X0;
 y0 = ns.y0 << Y0;
 z0 = ns.z0 << Z0;
 xyz0 = ns.xyz0 << Meq.Composer(x0,y0,z0);
 # Station 1
 X1 = 0.0;
 Y1 = 900.0;
 Z1 = 0.0;
 x1 = ns.x(s1=1) << X1;
 y1 = ns.y(s1=1) << Y1;
 z1 = ns.z(s1=1) << Z1;
 xyz1 = ns.xyz(s1=1) << Meq.Composer(x1,y1,z1);
 uvw1 = ns.uvw(s1=1) << Meq.UVW(radec=radec0,xyz_0=xyz0,xyz=xyz1);
 # Station 2
 X2 = 0.0;
 Y2 = 0.0;
 Z2 = 0.0;
 x2 = ns.x(s1=2) << X2;
 y2 = ns.y(s1=2) << Y2;
 z2 = ns.z(s1=2) << Z2;
 xyz2 = ns.xyz(s1=2) << Meq.Composer(x2,y2,z2);
 uvw2 = ns.uvw(s1=2) << Meq.UVW(radec=radec0,xyz_0=xyz0,xyz=xyz2);
 # Baseline
 myuvw = ns.uvw(s1=1,s2=2) << Meq.Subtract(uvw1,uvw2);

 # Define the factor of padding zeros to be added
 padfactor = 3.0;

 # Create the SixPack for the FITS Image
 # Image (Sixpack)
 home_dir = os.environ['HOME']
 infile_name = home_dir + '/Timba/WH/contrib/RJN/clean.fits'
 image_root = ns.image << Meq.FITSImage(filename=infile_name,cutoff=1.0);

 # Select the 4 Stokes planes
 # Selector (FourPack)
 iquv_root = ns.IQUV << Meq.Selector(children=image_root,multi=True,index=[2,3,4,5]);

 # Go from 4 Stokes planes to 4 Correlation planes
 # Stokes
 corr_root = ns.corr << Meq.Stokes(children=iquv_root);

 # FFT the 4 correlations
 fft_root = ns.fft << Meq.FFTBrick(children=corr_root,uvppw=padfactor);

 #UVInterpol
 interpol_root = ns.interpol << Meq.UVInterpolWave(Method=1,brick=fft_root,uvw=myuvw,additional_info=True);
 
 # Now create the 2 DFT nodes, to which we will compare the UVInterpol result.
 #
 #RA,Dec,RA_0,Dec_0
 ra_array1 = array([(4.356749)/0.001]);
 dec_array1=array([(1.092237)/0.001]);
 ra_polc1=meq.polc(coeff=ra_array1);
 dec_polc1=meq.polc(coeff=dec_array1);
 flux_array1 = array([1.5]);
 flux_polc1 = meq.polc(coeff=flux_array1);
 nRA_root1 = ns['nRA1']<<Meq.Parm(ra_polc1,node_groups='Parm');
 nDec_root1 = ns['nDec1']<<Meq.Parm(dec_polc1,node_groups='Parm');
 flux_root1 = ns['flux1']<<Meq.Parm(flux_polc1,node_groups='Parm');
 dRA_root = ns['dRA']<<Meq.Constant(0.001);
 dDec_root = ns['dDec']<<Meq.Constant(0.001);
 RA_root1 = ns['RA1']<<Meq.Multiply(children=[nRA_root1,dRA_root]);
 Dec_root1 = ns['Dec1']<<Meq.Multiply(children=[nDec_root1,dDec_root]);

 radec11 = ns.radec1(q='dft1') << Meq.Composer(RA_root1,Dec_root1);
 lmn1 = ns.lmn(q='dft1') << Meq.LMN(radec_0=radec0,radec=radec11);
 n1 = ns.n(q='dft1') << Meq.Constant(1.0);
 #n1 = ns.n(q='dft1') << Meq.Selector(children=lmn1,index=2);
 lmn11 = ns.lmn_minus1(q='dft1') << Meq.Paster(lmn1,n1-1,index=2);
 sqrtn1 = ns << Meq.Sqrt(n1);

 # DFT
 #dft_root = ns['DFT']<<Meq.Multiply(children=[Meq.Constant(-1.0),Meq.VisPhaseShift(lmn=lmn_root,uvw=myuvw)]);
 dft_root1 = ns['DFT1']<<Meq.VisPhaseShift(lmn=lmn11,uvw=myuvw);
 source_root1 = ns.source1<<Meq.Multiply(flux_root1,dft_root1);

 #RA,Dec,RA_0,Dec_0
 ra_array2 = array([(4.339685)/0.001]);
 dec_array2=array([(1.095365)/0.001]);
 ra_polc2=meq.polc(coeff=ra_array2);
 dec_polc2=meq.polc(coeff=dec_array2);
 flux_array2 = array([0.5]);
 flux_polc2 = meq.polc(coeff=flux_array2);
 nRA_root2 = ns['nRA2']<<Meq.Parm(ra_polc2,node_groups='Parm');
 nDec_root2 = ns['nDec2']<<Meq.Parm(dec_polc2,node_groups='Parm');
 flux_root2 = ns['flux2']<<Meq.Parm(flux_polc2,node_groups='Parm');
 #dRA_root = ns['dRA']<<Meq.Constant(0.001);
 #dDec_root = ns['dDec']<<Meq.Constant(0.001);
 RA_root2 = ns['RA2']<<Meq.Multiply(children=[nRA_root2,dRA_root]);
 Dec_root2 = ns['Dec2']<<Meq.Multiply(children=[nDec_root2,dDec_root]);

 radec12 = ns.radec12(q='dft2') << Meq.Composer(RA_root2,Dec_root2);
 lmn2 = ns.lmn(q='dft2') << Meq.LMN(radec_0=radec0,radec=radec12);
 n2 = ns.n(q='dft2') << Meq.Constant(1.0);
 #n2 = ns.n(q='dft2') << Meq.Selector(children=lmn2,index=2);
 lmn12 = ns.lmn_minus1(q='dft2') << Meq.Paster(lmn2,n2-1,index=2);
 sqrtn2 = ns << Meq.Sqrt(n2);

 # DFT
 #dft_root = ns['DFT']<<Meq.Multiply(children=[Meq.Constant(-1.0),Meq.VisPhaseShift(lmn=lmn_root,uvw=myuvw)]);
 dft_root2 = ns['DFT2']<<Meq.VisPhaseShift(lmn=lmn12,uvw=myuvw);
 source_root2 = ns.source2<<Meq.Multiply(flux_root2,dft_root2);

 pspredict = ns.pspredict << Meq.Add(source_root1,source_root2);

 # Compare the XX result between UVInterpol and DFT
 #
 # Condeq
 #
 # Select XX result plane from UVInterpol node
 select2_root = ns['Select2']<<Meq.Selector(children=interpol_root,multi=True,index=[0]);

 cond_root = ns['Condeq'] << Meq.Condeq(children=[select2_root,pspredict]);
 #cond_root = ns['Condeq'] << Meq.Condeq(children=[interpol_root,interpol2_root]);

 # Solve for the RA and / or Dec position of the source in the DFT branch
 # Solver
 solvables = [];
 solvables.append('nRA1');
 solvables.append('nDec1');
 solvables.append('flux1');
 solvables.append('nRA2');
 solvables.append('nDec2');
 solvables.append('flux2');
 #solvables.append('L');
 #solvables.append('M');
 solver_root = ns['Solver']<<Meq.Solver(children=[cond_root],num_iter=100,debug_level=20,solvable=solvables);

########################################################################

def _test_forest(mqs,parent,wait=False):

 # Create the Request Cells
 f0 = 1200.0e6
 f1 = 1500.0e6
 t0 = 0.0
 #t1 = 30.0
 t1 = 86400.0
 nfreq = 1
 ntime = 1000
 
 # create cell
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);

 # create request
 request1 = meq.request(cells=cells, eval_mode=0 );

 # And execute the Tree ...
 args=record(name='Solver', request=request1);
 mqs.meq('Node.execute', args, wait);
   

########################################################################

def _tdl_job_subtract(mqs,parent,wait=False):
 # srcnames is global: to be used inside _define_forest, _test_forest, and outside of them
 global srcnames   
 
 # Not sure why this is repeated here
 from Timba.Meq import meq

 # Create the Request Cells
 f0 = 1200.0e6
 f1 = 1500.0e6
 t0 = 0.0
 t1 = 86400.0
 nfreq = 1
 ntime = 1000
 
 # create cell
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);

 # create request
 request1 = meq.request(cells=cells, eval_mode=0 );

 # And execute the Tree ...
 args=record(name='Condeq', request=request1);
 mqs.meq('Node.execute', args, wait);

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  #display LSM without MeqBrowser
  #l.display(app='create')
