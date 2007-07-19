#!/usr/bin/python


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

script_name = 'MG_RJN_UVBrick_Patch.py'

# Short description:
#  The script produces visibility data (freq / time) for 1 baseline from
#  a UVBrick (in meters) that was created from a PatchComposer node.
#  The PatchComposer node creates an Image in frequency dependent l' / m'
#   coordinates. Input sources are taken from the file '3C343_nvss_small.txt'.
#   No LSM is used in order to make this script less dependent on changes
#   in other parts of the code.
#  The Stokes node goes from IQUV to XX XY YX YY
#  The FFTBrick node does the FFT, using a padding factor padfactor.
#   Since the input is in frequency dependent l'/m', the result is in
#   u / v coordinates in meters.
#  The UVInterpol node interpolates the UVBrick on the UVW data (in meters).


# Keywords: UVBrick, Patch, UVInterpol

# History:
# - 9 june 2006: creatiion:

#=======================================================================
# Import of Python / TDL modules:

import math
import random

from Timba.Contrib.RJN import RJN_sixpack
from Timba.Trees import JEN_bookmarks

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

# to force caching put 100
Settings.forest_state.cache_policy = 100


########################################################
def _define_forest(ns):  
    
 # Read the sources from a text file
 # The test_sources file contains only sources with zero flux strength. In this way a Patch of 
 #    certain extent is obtained. Later a non-zero flux source is added.
 #
 # please change this according to your setup
 home_dir = os.environ['HOME']
 infile_name = home_dir + '/Timba/WH/contrib/RJN/3C343_nvss_small.txt'
 infile=open(infile_name,'r')
 all=infile.readlines()
 infile.close()

 # regexp pattern
 pp=re.compile(r"""
   ^(?P<col1>\S+)  # column 1 'NVSS'
   \s*             # skip white space
   (?P<col2>[A-Za-z]\w+\+\w+)  # source name i.e. 'J163002+631308'
   \s*             # skip white space
   (?P<col3>\d+)   # RA angle - hr 
   \s*             # skip white space
   (?P<col4>\d+)   # RA angle - min 
   \s*             # skip white space
   (?P<col5>\d+(\.\d+)?)   # RA angle - sec
   \s*             # skip white space
   (?P<col6>\d+(\.\d+)?)   # eRA angle - sec
   \s*             # skip white space
   (?P<col7>\d+)   # Dec angle - hr 
   \s*             # skip white space
   (?P<col8>\d+)   # Dec angle - min 
   \s*             # skip white space
   (?P<col9>\d+(\.\d+)?)   # Dec angle - sec
   \s*             # skip white space
   (?P<col10>\d+(\.\d+)?)   # eDec angle - sec
   \s*             # skip white space
   (?P<col11>\d+)   # freq
   \s*             # skip white space
   (?P<col12>\d+(\.\d+)?)   # brightness - Flux
   \s*             # skip white space
   (?P<col13>\d*\.\d+)   # brightness - eFlux
   \s*
   \S+
   \s*$""",re.VERBOSE)


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

 lmax = 0
 mmax = 0
 linecount=0
 random.seed(0)
 srcnames = [];
 
 # read each source and add a Sixpack to the child_rec
 for eachline in all:
  v=pp.search(eachline)
  if v!=None:
   linecount+=1
   print v.group('col2'), v.group('col12')
   sname=v.group('col2')
   srcnames.append(sname)
   
   # Go from RA and Dec to radians
   source_RA=float(v.group('col3'))+(float(v.group('col5'))/60.0+float(v.group('col4')))/60.0
   source_RA*=math.pi/12.0
   source_Dec=float(v.group('col7'))+(float(v.group('col9'))/60.0+float(v.group('col8')))/60.0
   source_Dec*=math.pi/180.0

   #sisif = math.log10( eval(v.group('col12')) )
   sisif = eval(v.group('col12')) 
   
   # Definition of Q%, U%, V%
   qin = random.uniform(-0.2,0.2)
   uin = random.uniform(-0.2,0.2)
   vin = random.uniform(-0.01,0.01)

   sixroot = RJN_sixpack.make_sixpack(srcname=sname,RA=source_RA,Dec=source_Dec,ISIF0=sisif,Qpct=qin,Upct=uin,Vpct=vin,ns=ns)

   sixname = 'sixpack[q='+sname+']';
   child_rec.append(sixname);

   # Determine the size of the grid. Hence, determine larges l and m values. 
   lc = -math.cos(source_Dec)*math.sin(RA_0-source_RA)
   lm = math.cos(Dec_0)*math.sin(source_Dec) - math.sin(Dec_0)*math.cos(source_Dec)*math.cos(RA_0-source_RA)
   
   lmax = max(lmax,abs(lc))
   mmax = max(mmax,abs(lm))
 
 
 print "Inserted %d sources" % linecount 
 print "maximum l and m out of Phase Center", lmax, mmax

 # At this point the Phase Center and all sources are combined into a "source list": child_rec.

 # Define the factor of padding zeros to be added
 padfactor = 3.0;

 # Create the SixPack for the Patch Image
 # PatchComposer (SixPack)
 patch_root = ns.patch << Meq.PatchComposer(children=child_rec,uvppw=padfactor,max_baseline=2700.0);

 # Select the 4 Stokes planes
 #Selector (FourPack)
 iquv_root = ns.IQUV << Meq.Selector(children=patch_root,multi=True,index=[2,3,4,5]);

 # Go from 4 Stokes planes to 4 Correlation planes
 #Stokes
 corr_root = ns.corr << Meq.Stokes(children=iquv_root);

 # FFT the 4 correlations
 #FFTBrick
 fft_root = ns.fft << Meq.FFTBrick(children=corr_root,uvppw=padfactor);

 # The actual Interpolation
 #  Method = 1: Bi-Cubic Hermite Interpolation (most accurate)
 #  Method = 2: 4th order polynomial interpolation
 #  Method = 3: Bi-linear interpolation
 #
 # If (Additional_Info = True) the UV interpolation tracks are plotted on the UV plane
 #
 #UVInterpol
 interpol_root = ns.interpol << Meq.UVInterpol(Method=1,brick=fft_root,uvw=myuvw,additional_info=True);
 

 # Define Bookmarks
 JEN_bookmarks.create(corr_root,page="Patch Image",viewer="Result Plotter");
 JEN_bookmarks.create(fft_root,page="UVBrick",viewer="Result Plotter");
 JEN_bookmarks.create(interpol_root,udi="cache/result/uvinterpol_map",page="UVBrick",viewer="Result Plotter");
 JEN_bookmarks.create(patch_root,page="Patch Image",viewer="Result Plotter");
 JEN_bookmarks.create(interpol_root,page="Freq Time Result",viewer="Result Plotter");

########################################################################

def _test_forest(mqs,parent):

 # Create the Request Cells
 f0 = 1350.0e6
 f1 = 1450.0e6
 t0 = 0.0
 t1 = 86400.0
 nfreq = 4
 ntime = 100
 
 # create cell
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);

 # create request
 request1 = meq.request(cells=cells, eval_mode=0 );

 # And execute the Tree ...
 args=record(name='interpol', request=request1);
 mqs.meq('Node.execute', args, wait=False);
   

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
