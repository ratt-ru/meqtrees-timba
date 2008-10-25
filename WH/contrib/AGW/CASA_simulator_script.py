# CASA script that uses the CASA simulator to create
# UV tracks for SKA simulations

import random
import numpy
import os

# basic parameters - things which are most likely to be changed
observatory  = 'VLA'         # where the telescope is situated
RA0          = "0h7m0.0"     # field centre RA
DEC0         = "33d00m00s"   # field centre DEC
Freq         = "1400MHz"     # frequency at lower edge of band
num_channels = 16            # number of channels
channel_inc  = '5.0MHz'      # channel increment
Diameter     = 25.0          # dish diameter in metres
num_dishes   = 30            # number of dishes in the array
Stokes       = 'RR,RL,LR,LL' # Stokes parameters - other option is 'XX,XY,YX,YY'
int_time     = '60s'         # integration period
ref_time = me.epoch('IAT','2007/01/01')  # a reference time
starttime    = -14400.0      # start of obs, in seconds relative to ref_time
scanlength   =  28800.0      # length of observation, in sec
noise        =  '0.1Jy'      # add some noise. Use '0.0Jy' if no noise wanted
FOV          =  5            # field of view in arcmin
num_sources  = 10            # number of sources to observe, randomized over FOV

clname = 'mymodel.cl'        # file for component list
msname = 'CASA_demo.MS'      # name of measurement set to create

# first delete old MS, test images, etc
print '*** deleting previous stuff ***'
os.system("/bin/rm -rf CASA_demo.MS mymodel.cl")

# create sources with randomized offsets from field centre
dec_offset=[]
ra_offset=[]
for i in range(num_sources):
  offset = random.uniform(-FOV, FOV)
  dec_offset.append(str(offset)+'arcmin')
  offset = random.uniform(-FOV, FOV)
  ra_offset.append(str(offset)+'arcmin')

# now add above offsets to field centre
refRA = qa.unit(RA0);
refDec = qa.unit(DEC0);
for i in range(num_sources):
  ra = qa.add(refRA,ra_offset[i]);
  dec = qa.add(refDec,dec_offset[i]);
  direction = me.direction(rf='J2000',v0=ra,v1=dec)
  cl.addcomponent(dir=direction,flux=1.0, freq=Freq)

# the setspectrum function seems to be broken
# cl.setspectrum(0, 'spectral index', [-0.5, 0, 0, 0])

cl.rename(filename=clname)
cl.done()

#  Define SKA array, antenna locations from Tim Cornwell, local coordinates
    
xx = [-1398.518311, -2799.947754, -43.786434, -1252.077026, 2197.975342, -2422.707520, 3586.145508, 1012.639587, -2161.428467, -1074.882935, 3769.756104, 360.050232, -2489.192871, -1158.198242, -400.231628, -2931.127686, -975.114929, -2974.646484, 237.993591, -360.298035, 2746.886963, 1342.838989, 2092.018066, -624.790771, 3048.720459, -666.824524, 71.983940, 770.071899, -538.815735, 2862.588867]

yy = [-121.947021, 852.765686, 265.848907, 2375.637451, 2126.479248, 1123.350830, 844.697083, -3248.580566, -2382.272949, -3590.418213, 336.745850, -3556.010498, -1293.422974, 941.583923, 420.135803, 643.004700, -654.646118, -43.957832, 1082.475098, -183.253159, 1995.818237, 2669.032959, -3323.141357, -1419.005981, -791.578369, 822.521667, 3144.392090, -105.612885, -1600.316528, -2682.874512]

zz = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

diam = numpy.zeros((num_dishes,), numpy.float64) + Diameter;
sm.open(msname)
print 'opened MS'
sm.setspwindow(spwname='SKA', freq=Freq,
		      deltafreq=channel_inc, freqresolution=channel_inc, 
		      nchannels=num_channels, stokes=Stokes)
posvla = me.observatory(observatory);
sm.setconfig(telescopename=observatory, 
       x=xx, y=yy,z=zz, dishdiameter=diam.tolist(), mount='ALT-AZ',
       coordsystem='local', referencelocation=posvla)

dir0 = me.direction("J2000",  RA0, DEC0)
sm.setfield(sourcename='test_image', sourcedirection=dir0)
sm.settimes(integrationtime=int_time, usehourangle=True, referencetime=ref_time)
sm.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
sm.setauto(autocorrwt=0.0)

scan=0
endtime = starttime + scanlength
while(starttime<endtime):
  print ' **** observing'
  sm.observe('test_image', 'SKA', starttime=str(starttime)+'s', 
                                  stoptime=str(starttime+scanlength)+'s')
  me.doframe(ref_time)
  me.doframe(posvla)
  hadec=me.direction('hadec', qa.time(str(starttime+scanlength/2)+'s'), DEC0)
  azel=me.measure(hadec,'azel')
  sm.setdata(msselect='SCAN_NUMBER=='+ str(scan))
  print ' **** predicting'
  sm.predict(complist=clname)
  starttime=starttime+scanlength
  scan=scan+1

if noise != '0.0Jy':
  print ' **** corrupting'
  sm.setnoise(mode='simplenoise', simplenoise=noise)
  sm.corrupt();

sm.done()
