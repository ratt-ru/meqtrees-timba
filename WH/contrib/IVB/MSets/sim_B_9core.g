# glish script that uses newsimulator to simulate a 14 station
# SKA located at the VLA site consisting of 250m dishes.

RA0          := '0h7m0.0';
#DEC0         := '33d00m00s';
DEC0         := '20d00m00s';
#DEC0         := '70d00m00s';
Freq         := '73.25MHz';
Diameter     := 25.0;
holderdir    := './';
msoutname    := 'VLA_B_9core.MS'

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
    
    mysim.setspwindow(spwname='SKA', freq=freq,
		      deltafreq='1.5MHz', freqresolution='1.5MHz', 
		      nchannels=1, stokes='XX XY YX YY');
    
    note('Simulating VLSS');
    posvla := dm.observatory('vla');

#  Define SKA 'C' array, == VLA 'C' array scaled by factor 10, local coordinates
#  Use every second antenna -> a 14 antenna array, so equals number of 
#  antennas in WSRT array - should be easy to adapt WSRT trees, etc
#
#
## VLA -- central 9 dishes, B-array, ENU coordinates
#
	xx := [-122.026001, -401.255005, -804.578003, 133.658005, 438.691986, 
	   	879.594971, -11.756400, -38.032001, -76.320198]
	yy := [-82.291059, -270.640396, -542.687495, -62.264433, -204.492799, 
	  	-410.076443, 134.352948, 434.716353, 871.780462]
	zz := [1.002049, 1.365641, 2.558356, 0.910065, -0.151419, 
		-0.342958, 0.600608, -0.000561, -0.933747]

# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := 9
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

    starttime:=-2250.0;
    scanlength:=4500.0
    scan:=1;
    while(starttime<2250) {
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
#shell('rm -rf single-channel-2min-VLSS.MS mymodel.cl')
#print '*** calling mkcomplist ***'
#num_sources := 1
#mkcomplist(num_sources,flux,ra,dec);
#print '*** calling mkcomps ***'
#mkcomps('mymodel.cl',flux,ra,dec);
print '*** calling simms ***'
simms(msoutname,'mymodel.cl');
exit

