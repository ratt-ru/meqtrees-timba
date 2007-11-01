# glish script that uses newsimulator to simulate a 14 station
# SKA located at the VLA site consisting of 250m dishes.

RA0          := '0h7m0.0';
#DEC0         := '33d00m00s';
DEC0         := '20d00m00s';
#DEC0         := '70d00m00s';
Freq         := '73.25MHz';
Diameter     := 25.0;
holderdir    := './';
msoutname    := 'VLSS_1h.MS'

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

#
## vla -- B array, VLA local coordinates XY // equatorial plane, Z=north, X through array center
#
#      xx:=[-2629.09,35.6424,560.138,1005.46,-2091.42,114.458,1534.60,306.203,-1660.44,
#    1316.47,46.9401,1253.27,2000.10,733.392,-1174.29,-801.383,998.680,-74.7845,
#    -489.258,1640.07,377.029,152.779,499.857,765.251,-3217.56,-243.585,229.494]
#
#      yy:=[-410.674,133.658,2113.24,-2643.00,-326.600,438.692,5793.91,-804.578,
#    -259.404,-3443.31,-122.026,4733.62,-5299.78,-1932.98,-183.339,-124.993,3764.32,
#    -11.7564,-76.3202,-4329.94,1441.00,-401.255,-1317.99,2889.45,-502.651,-38.0320,879.595]
#
#      zz:=[3885.63,-51.0618,-810.675,-1472.17,3089.43,-169.460,-2223.47,-448.058,
#    2454.47,-1913.51,-67.5977,-1816.88,-2962.86,-1078.09,1734.24,1182.14,-1443.43,
#    111.617,721.546,-2416.68,-556.107,-223.398,-735.197,-1108.87,4756.15,360.062,-339.846]
#
## vla -- B array, ENU coordinates: X=east, Y=north, Z=up
#
	xx := [-410.674011, 133.658005, 2113.239990,-2643.000000, -326.600006, 
		438.691986, 5793.910156, -804.578003, -259.403992,-3443.310059, 
		-122.026001, 4733.620117,-5299.779785,-1932.979980, -183.339005, 
		-124.992996, 3764.320068, -11.756400, -76.320198,-4329.939941, 
		1441.000000, -401.255005,-1317.989990, 2889.449951, -502.651001, 
		-38.032001, 879.594971]
	yy := [4691.506597, -62.264433, -985.319455,-1782.742893, 3730.765772, 
		-204.492799,-2701.514661, -542.687495, 2963.356819,-2322.559509, 
		-82.291059,-2207.110999,-3574.762548,-1303.890544, 2094.407950, 
		1428.169400,-1755.139381, 134.352948, 871.780462,-2920.642564, 
		-671.867092, -270.640396, -889.026106,-1347.236224, 5742.269118, 
		434.716353, -410.076443]
	zz := [-0.360965, 0.910065, 9.699878, 7.891142, -1.159715, 
 		-0.151419, 25.185900, 2.558356, 0.020878, 18.195268, 
		1.002049, 19.993346, -3.556969, 3.360327, -0.882298, 
		-1.372830, 18.379324, 0.600608, -0.933747, 4.282161, 
		0.678300, 1.365641, 2.063512, 12.501156, 0.005605, 
		-0.000561, -0.342958]
#
# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := 27
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
#shell('rm -rf single-channel-2min-VLSS.MS mymodel.cl')
#print '*** calling mkcomplist ***'
#num_sources := 1
#mkcomplist(num_sources,flux,ra,dec);
#print '*** calling mkcomps ***'
#mkcomps('mymodel.cl',flux,ra,dec);
print '*** calling simms ***'
simms(msoutname,'mymodel.cl');
exit

