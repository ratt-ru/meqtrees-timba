# glish script to simulate LOFAR with any number of antennae
# at the location of WSRT

# The main input parameters
# Phase center
RA0          := '7h0m00.0';
DEC0         := '50d00m00s';
epoch0       := '2000/01/01';

# Frequency and BW
Frequency    := 60 #Central frequency in MHz
Freq_unit    := 'MHz'
BW_digit     := 4  #Total bandwith in MHz
BW_unit      := 'MHz'
n_chan       := 8

# Time settings for the observations
t_int	     := '20s'# integration time per scan (NB this is a string!)
t_obs        := 1200  # total observing time in seconds

# Basename for file and spectral window
basename     := 'LO'
goalname    := 'HHsim'
# Where the MS goes
holderdir    := '/data/bemmel/MSets/';

#Dishes (equivalent collecting area for LOFAR)
#In principle I can simulate 49-LOFAR and select a subset of antennas
#in MeqTree. Since the stations are in the proper order this should
#reflect the smaller LOFAR.
NN	     := 20

# Derived settings
# Station diameter as per Ronald Nijboers station footprints
# For LBA:
if ( Frequency == 15){Diameter := 85}
if ( Frequency == 30){Diameter := 85}
if ( Frequency == 45){Diameter := 65}
if ( Frequency == 60){Diameter := 45}
if ( Frequency == 75){Diameter := 45}
# For HBA without splitting core station into 2x35m
# Can I implement different diameters for different stations?
if ( Frequency == 120){Diameter := 50}
if ( Frequency == 150){Diameter := 50}
if ( Frequency == 180){Diameter := 50}
if ( Frequency == 210){Diameter := 50}
if ( Frequency == 240){Diameter := 50}

# Frequency
Freq_digit   := Frequency-BW_digit/2;
Freq         := spaste(Freq_digit,Freq_unit);
BW	     := spaste(BW_digit,BW_unit);
# Per channel frequency width
CW_digit := BW_digit/n_chan
CW       := spaste(CW_digit,BW_unit)

print '****************************************************'
print 'Starting frequency = ',Freq
print 'Central frequency = ', Frequency
print 'Total bandwidth = ',BW
print 'Channel incremenet = ',CW
print '****************************************************'

# Central frequency (need to calculate this from BW and Freq)
# Start and end time
# NB: source goes through the meridian half-way through the obs-time.
# This should be adjusted if low-elevation fields are simulated.
t_start      := -t_obs/2
t_end        := t_obs/2
# Some derived names
specname     := spaste(basename,NN)
msoutname    := spaste(specname,"_",goalname,"_",Frequency,"_",BW,"_",t_obs,"_",t_int,".MS")

## LOFAR full ENU coordinates (X=north, Y=east, Z=up)
if ( NN == 49){
 xx:= [83.3300,-107.1400,-25.7500,108.6200,-213.8900,311.5400,-339.3000,
     304.8700,-576.9000,-768.1000,-673.8900,874.6200,-121.9600, -1340.0000, 
     -1320.0000, -8560.0000,-12470.0000,4260.0000,3050.0000,6600.0000,-32.0000,
     33.0300,-143.4700,810.4300,722.8700, -4250.0000,2750.0000, -8050.0000, 
     15650.0000,7760.0000,-21990.0000, 36980.0000,-24000.0000, -5000.0000, 
     -3770.0000, 70000.0000, 34000.0000,-56800.0000,2150.0000,4100.0000,
     7650.0000, 20000.0000,3850.0000,-146.5500,-51.8900,-269.8000,-956.6300,
     233.2900,-298.1000]
 yy:= [-205.9000,-82.2100,-294.2400,230.4900,126.1500,-479.0400,-255.7200,
     -955.0400,729.7300,129.6000,-469.1800,-428.1700, -1211.7200, -1720.0000,
     2970.0000, -3100.0000,-12930.0000,3250.0000, -6252.0000, 35000.0000,
     -175.0000,-74.8600,-217.7900,28.3900,660.9600,1250.0000,8400.0000, 
     11150.0000,1720.0000,-17550.0000,-11750.0000, -9820.0000,-39000.0000, 
     53000.0000,-68540.0000, -7700.0000,-37000.0000,-19400.0000,1850.0000, 
     -2000.0000, -4550.0000, -8600.0000,-27350.0000,-587.1800,-426.5100,
     -126.3700,-281.7200,-297.5100,1070.2700]
 zz:= [ 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000]
	} 
# LOFAR full 36 stations
if ( NN == 36){ 
 	xx:= [83.3300,-107.1400,-25.7500,108.6200,-213.8900,311.5400,-339.3000,
     304.8700,-576.9000,-768.1000,-673.8900,874.6200,-121.9600, -1340.0000, 
     -1320.0000, -8560.0000,-12470.0000,4260.0000,3050.0000,6600.0000,-32.0000,
     33.0300,-143.4700,810.4300,722.8700, -4250.0000,2750.0000, -8050.0000, 
     15650.0000,7760.0000,-21990.0000, 36980.0000,-24000.0000, -5000.0000, 
     -3770.0000, 70000.0000]
 	yy:= [-205.9000,-82.2100,-294.2400,230.4900,126.1500,-479.0400,-255.7200,
     -955.0400,729.7300,129.6000,-469.1800,-428.1700, -1211.7200, -1720.0000,
     2970.0000, -3100.0000,-12930.0000,3250.0000, -6252.0000, 35000.0000,
     -175.0000,-74.8600,-217.7900,28.3900,660.9600,1250.0000,8400.0000, 
     11150.0000,1720.0000,-17550.0000,-11750.0000, -9820.0000,-39000.0000, 
     53000.0000,-68540.0000, -7700.0000]
 	zz:= [ 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000]
    }
if ( NN == 31){
 	xx:= [83.3300,-107.1400,-25.7500,108.6200,-213.8900,311.5400,-339.3000,
     304.8700,-576.9000,-768.1000,-673.8900,874.6200,-121.9600, -1340.0000, 
     -1320.0000, -8560.0000,-12470.0000,4260.0000,3050.0000,6600.0000,
     -4250.0000,2750.0000, -8050.0000, 15650.0000,7760.0000,-21990.0000, 
     36980.0000,-24000.0000, -5000.0000, -3770.0000, 70000.0000]
 	yy:= [-205.9000,-82.2100,-294.2400,230.4900,126.1500,-479.0400,-255.7200,
     -955.0400,729.7300,129.6000,-469.1800,-428.1700, -1211.7200, -1720.0000,
     2970.0000, -3100.0000,-12930.0000,3250.0000, -6252.0000, 35000.0000,
     1250.0000,8400.0000, 11150.0000,1720.0000,-17550.0000,-11750.0000, 
     -9820.0000,-39000.0000, 53000.0000,-68540.0000, -7700.0000]
 	zz:= [ 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000]
}
if ( NN == 20){
 	xx:= [83.3300,-107.1400,-25.7500,108.6200,-213.8900,311.5400,-339.3000,
     304.8700,-576.9000,-768.1000,-673.8900,874.6200,-121.9600, -1340.0000, 
     -1320.0000, -8560.0000,-12470.0000,4260.0000,3050.0000,6600.0000]
 	yy:= [-205.9000,-82.2100,-294.2400,230.4900,126.1500,-479.0400,-255.7200,
     -955.0400,729.7300,129.6000,-469.1800,-428.1700, -1211.7200, -1720.0000,
     2970.0000, -3100.0000,-12930.0000,3250.0000, -6252.0000, 35000.0000]
 	zz:= [ 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
     0.0000, 0.0000, 0.0000]
}

#-----------------------------------------------------------------------
#
simms:=function(msname,clname,freq=Freq,noise='0.0Jy',dovp=F,setoffsets=F,
		      RA=RA0,Dec=DEC0)
{
    include 'newsimulator.g';

    simclname:= spaste(holderdir, '/',clname);
    simmsname:= spaste(holderdir, '/',msname);
    
    
    note('Create the empty measurementset');
    
    mysim := newsimulator(msname);
    
    mysim.setspwindow(spwname=specname, freq=freq,
		      deltafreq=CW, freqresolution=CW, 
		      nchannels=n_chan, stokes='XX XY YX YY');
    
    note('Simulating VLSS');
    posvla := dm.observatory('wsrt');

#
# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := NN
    diam := 0.0 * [1:num_dishes] + Diameter;
    mysim.setconfig(telescopename='LOFAR', 
		    x=xx, y=yy, z=zz,
		    dishdiameter=diam, 
		    mount='alt-az', antname='LOFAR',
		    coordsystem='local', 
		    referencelocation=posvla);

    dir0    := dm.direction('j2000',  RA, Dec);
    mysim.setfield(sourcename='test_image', 
		   sourcedirection=dir0)

    ref_time := dm.epoch('iat', epoch0);
    mysim.settimes(integrationtime=t_int, usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

    starttime:=t_start;
    scanlength:=t_obs
    scan:=1;
    while(starttime<t_end) {
      mysim.observe('test_image', specname,
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
print '*** deleting previous stuff ***'
comm :=spaste('rm -rf ',msoutname)
shell(comm)
#print '*** calling mkcomplist ***'
#num_sources := 1
#mkcomplist(num_sources,flux,ra,dec);
#print '*** calling mkcomps ***'
#mkcomps('mymodel.cl',flux,ra,dec);
print '*** calling simms ***'
simms(msoutname,'mymodel.cl');
print 'Writen new MS named ',msoutname,' in ',holderdir
exit

