# glish script that uses newsimulator to simulate a 14 station
# SKA located at the VLA site consisting of 250m dishes.

# Hardcoded settings
# Phase center
RA0          := '0h7m0.0';
DEC0         := '45d00m00s';

# Number of dishes and collecting area
NN           := 18   # number of stations/dishes
Diameter     := 50.0; # equivalent collecting area of station

# Observing parameters 
# Central frequency of observing band
CFreq        := '60MHz';
# Start frequency of observing band 
# How can I calculate the starting frequency?
# It needs to be a string of (CFreq-deltafreq/2.0)MHz
Freq         := '59.25MHz'
# Below stuff doesn't work
#Freq         := spaspte(nu - (deltafreq/2.0),"MHz")
# Integration time
t_int        := '120s'
# Channel width and separation
deltafreq    := '1.5MHz'  # width
freqres      := deltafreq # separation
# Number of channels
nchannels    := 1
# Starting time (from RA0 in seconds)
t_start      := -1800
# Total observing time (in seconds)
t_obs 	     := 3600

# Location of the Measurement set
holderdir    := '/Users/bemmel/MeqTree/MSets/';
basename     := 'LOcore'
mynote       := spaste('Simulating LOFAR ',NN,' station core')

# Derived settings for 
# End time of scan
t_end        := scanlength-t_start
# Spectral window name
specname     := spaste(basename,NN)
# Name of the MS, which is defined as:
# specname+Freq+deltafreq+t_obs+t_int.MS
msoutname    := spaste(specname,"_",CFreq,"_",deltafreq,"_",t_obs,"_",t_int,".MS")

print "MS name is ", msoutname
print "SPWindow name is ", specname
print mynote
print Freq

#-----------------------------------------------------------------------
#Do I need to put this inside the simms function, or will it work from here?
# Can I read this from file?
#
## LOFAR core ENU coordinates (X=north, Y=east, Z=up)
#
 xx:= [-32.0000,83.3300,33.0300,-107.1400,-143.4700,-25.7500,-213.8900,
        -339.3000,304.8700,-576.9000,-673.8900,874.6200,-121.9600,108.6200,
        311.5400,810.4300,-768.1000,722.8700]
 yy:= [-175.0000,-205.9000,-74.8600,-82.2100,-217.7900,-294.2400,126.1500,
       -255.7200,-955.0400,729.7300,-469.1800,-428.1700, -1211.7200,
       230.4900,-479.0400,28.3900,129.6000,660.9600]
 zz:= [ 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
        0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
        0.0000, 0.0000]



#
simms:=function(msname,clname,freq=Freq,noise='0.0Jy',dovp=F,setoffsets=F,
		      RA=RA0,Dec=DEC0)
{
    include 'newsimulator.g';

    simclname:= spaste(holderdir, '/',clname);
    simmsname:= spaste(holderdir, '/',msname);
    
    
    note('Create the empty measurementset');
    
    mysim := newsimulator(msname);
    
    mysim.setspwindow(spwname='LOFAR', freq=Freq,
		      deltafreq='1.5MHz', freqresolution='1.5MHz', 
		      nchannels=1, stokes='XX XY YX YY');
    
    note('Simulating VLSS');
    posvla := dm.observatory('vla');

####

# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := 18
    diam := 0.0 * [1:num_dishes] + Diameter;
    mysim.setconfig(telescopename='VLA', 
		    x=xx, y=yy, z=zz,
		    dishdiameter=diam, 
		    mount='alt-az', antname='VLA',
		    coordsystem='local', 
		    referencelocation=posvla);

    dir0    := dm.direction('j2000',  RA, Dec);
    mysim.setfield(sourcename='test_image', 
		   sourcedirection=dir0)

    ref_time := dm.epoch('iat', '2001/01/01');
    mysim.settimes(integrationtime='120s', usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

    starttime:=-1800.0;
    scanlength:=3600.0
    scan:=1;
    while(starttime<1800) {
      mysim.observe('test_image', 'SKA',
		    starttime=spaste(starttime, 's'),
		    stoptime=spaste(starttime+scanlength,'s'));
      dm.doframe(ref_time);
      dm.doframe(posvla);
      print "Scan", scan;
      hadec:=dm.direction('hadec', dq.time(spaste(starttime+scanlength/2,'s')),
			  DEC0);
      print 'HADec: ', dm.dirshow(hadec);
      azel:=dm.measure(hadec,'azel');
      print 'AzEl:  ', dm.dirshow(azel);
      mysim.setdata(msselect=spaste('SCAN_NUMBER==',scan-1));
      mysim.predict(complist=simclname);
      starttime+:=scanlength;
      scan+:=1;
    }

    if (noise != '0.0Jy')
    {
 	mysim.setnoise(mode='simplenoise', simplenoise=noise);
 	mysim.corrupt();
    }

    mysim.done();
}

# to do a run ...
# first delete old MS, test images, etc
#print '*** deleting previous stuff ***'
comm := spaste('rm -rf ',msoutname)
shell(comm)
#print '*** calling mkcomplist ***'
#num_sources := 1
#mkcomplist(num_sources,flux,ra,dec);
#print '*** calling mkcomps ***'
#mkcomps('mymodel.cl',flux,ra,dec);
print '*** calling simms ***'
simms(msoutname,'mymodel.cl');
exit

