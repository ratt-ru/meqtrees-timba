#!/usr/bin/python

script_name = 'MG_RJN_UVBrick_FITS.py'

# Short description:
#  The script produces visibility data (freq / time) for 1 baseline from
#  a UVBrick (in wavelengths) that was created from a FITSImage node.
#  The FITSImage node creates an Image in l / m coordinates.
#  The Stokes node goes from IQUV to XX XY YX YY
#  The FFTBrick node does the FFT, using a padding factor padfactor.
#   Since the input is l / m, the result is in u / v coordinates in
#   wavelengths.
#  The UVInterpolwave node interpolates the UVBrick on the UVW data
#   (in wavelengths).


# Keywords: UVBrick, FITSImage, UVInterpolWave

# History:
# - 9 june 2006: creatiion:

#=======================================================================
# Import of Python / TDL modules:

import math
import random

from Timba.Trees import JEN_bookmarks

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

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
 padfactor = 30.0;

 # Create the SixPack for the FITS Image
 # Image (Sixpack)
 home_dir = os.environ['HOME']
 infile_name = home_dir + '/LOFAR/Timba/WH/contrib/RJN/source1a.fits'
 image_root = ns.image << Meq.FITSImage(filename=infile_name,cutoff=1.0);

 # Select the 4 Stokes planes
 #Selector (FourPack)
 iquv_root = ns.IQUV << Meq.Selector(children=image_root,multi=True,index=[2,3,4,5]);

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
 interpol_root = ns.interpol << Meq.UVInterpolWave(Method=1,brick=fft_root,uvw=myuvw,additional_info=True);
 

 # Define Bookmarks
 JEN_bookmarks.create(corr_root,page="Image",viewer="Result Plotter");
 JEN_bookmarks.create(fft_root,page="UVBrick",viewer="Result Plotter");
 JEN_bookmarks.create(interpol_root,udi="cache/result/uvinterpol_map",page="UVBrick",viewer="Result Plotter");
 JEN_bookmarks.create(image_root,page="Image",viewer="Result Plotter");
 JEN_bookmarks.create(interpol_root,page="Freq Time Result",viewer="Result Plotter");

########################################################################

def _test_forest(mqs,parent):

 # Create the Request Cells
 f0 = 1350.0e6
 f1 = 1450.0e6
 t0 = 0.0
 t1 = 86400.0
 nfreq = 1
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
  
