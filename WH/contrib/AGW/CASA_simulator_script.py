# An  adaption of the glish simulator scripts that uses the CASA simulator 
# to create UV tracks for SKA simulations

import random
import numpy
import os

RA0          = "0h7m0.0"
DEC0         = "33d00m00s"
Freq         = "800MHz"
Diameter     = 25.0
clname = "mymodel.cl"
msname = "CASA_demo.MS"
holderdir    = './';

# first delete old MS, test images, etc
print '*** deleting previous stuff ***'
os.system("/bin/rm -rf CASA_demo.MS mymodel.cl")

# create a unit source at field centre so we have something to observe
# and add to component list
direction = "J2000 " + RA0 + " " + DEC0
print 'direction ', direction
cl.addcomponent(dir=direction, flux=1.0, freq=Freq)

#************** can't get the following line to work
#cl.setspectrum(which=0, type='spectral index', index=[0.0,0.0,0.0,0.0])

cl.rename(filename=clname)
cl.done();

#  Define SKA 'C' array, == VLA 'C' array scaled by factor 10, local coordinates
#  Use every second antenna -> a 14 antenna array, so equals number of 
#  antennas in WSRT array - should be easy to adapt WSRT trees, etc

xx = [4110.100006,1340.110001,2680.309998,4390.410004,6440.210022,8800.309998,
     11470.10999,14420.41003,17650.41003,-360.7900009,-1210.690002,-2440.789993,
     -4010.190002,-5880.48999,-8040.690002,-10480.48999,-13180.48999,-16130.98999,
     -40.38999987,-110.29,-220.7900009,-370.6899986,-550.3899994,-750.8899994,
     -990.0899963,-1240.690002,-1520.690002]  

#    xx = [4110.100006,2680.309998,6440.210022, 11470.10999,17650.41003,-1210.690002,
# -4010.190002,-8040.690002,-13180.48999, -40.38999987,-220.7900009,-550.3899994,
# -990.0899963,-1520.690002]


yy =[30.51999998,-390.8300018,-1020.480003,-1820.149994,-2770.589996,-3870.839996,
     -5120.119995,-6490.76001,-8000.450012,-20.58999991,-590.9099998,-1420.889999,
     -2480.410004,-3740.690002,-5200.599976,-6850,-8670.099976,-10660.42004,770.1500015,
     1560.910004,2870.980011,4570.429993,6600.409973,8940.700012,11580.82996,14510.43005,
     17710.48999]  

#   yy =[30.51999998,-1020.480003,-2770.589996, -5120.119995,-8000.450012,-590.9099998,
# -2480.410004,-5200.599976,-8670.099976,770.1500015,
# 2870.980011,6600.409973,11580.82996, 17710.48999]  

zz = [0.25,-0.439999998,-1.46000004,-3.77999997,-5.9000001,-7.28999996,
     -8.48999977,-10.5,-9.56000042,0.25,-0.699999988,-1.79999995,-3.28999996,
     -4.78999996,-6.48999977,-9.17000008,-12.5299997,-15.3699999,1.25999999,
     2.42000008,4.23000002,6.65999985,9.5,12.7700005,16.6800003,21.2299995,
     26.3299999]  

#   zz = [00.25,-10.46000004,-50.9000001, -80.48999977,-90.56000042,-00.699999988,-30.28999996,
# -60.48999977,-120.5299997,10.25999999, 40.23000002,90.5,160.6800003, 260.3299999]  
    
num_dishes = len(xx)
diam = numpy.zeros((num_dishes,), numpy.float64) + Diameter;
sm.open(msname)
print 'opened MS'
sm.setspwindow(spwname='SKA', freq=Freq,
		      deltafreq='38.0MHz', freqresolution='38.0MHz', 
		      nchannels=16, stokes='RR,RL,LR,LL');
posvla = me.observatory('VLA');
sm.setconfig(telescopename='VLA', 
       x=xx, y=yy,z=zz, dishdiameter=diam.tolist(), mount='ALT-AZ',
       coordsystem='local', referencelocation=posvla)

dir0 = me.direction("J2000",  RA0, DEC0)

sm.setfield(sourcename='test_image', sourcedirection=dir0)

ref_time = me.epoch('IAT', '2001/01/01');
sm.settimes(integrationtime='60s', usehourangle=True, referencetime=ref_time);

sm.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
sm.setauto(autocorrwt=0.0);

starttime=-14400.0;
scanlength=28800.0
scan=0;
while(starttime<14400):
      print '**** observing'
      sm.observe('test_image', 'SKA',
		    starttime=str(starttime)+'s',
		    stoptime=str(starttime+scanlength)+'s');
      me.doframe(ref_time);
      me.doframe(posvla);
      hadec=me.direction('hadec', qa.time(str(starttime+scanlength/2)+'s'),
			  DEC0);
      print 'HADec: ', me.dirshow(hadec);
      azel=me.measure(hadec,'azel');
      print 'AzEl:  ', me.dirshow(azel);
      sm.setdata(msselect='SCAN_NUMBER=='+ str(scan));
      print '**** predicting'
      sm.predict(complist=clname);
      starttime=starttime+scanlength;
      scan=scan+1
sm.done();
