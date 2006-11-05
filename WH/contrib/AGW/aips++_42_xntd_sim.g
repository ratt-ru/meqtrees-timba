# glish script that uses newsimulator to simulate a 30 station
# xNTD located at the ATCA site consisting of 12m dishes.
# We observe a single  source at-42 deg DEC, but the phase tracking
# centre is at -45 deg DEC.

RA0          := '0h7m0.0';
DEC0         := '-45d00m00s';
Freq         := '1400MHz';
Diameter     := 12.0;
holderdir    := './';

#
#-----------------------------------------------------------------------
#
mkcomps:=function(clname='model.cl')
{
    include 'componentlist.g';
    local f;
    cl:=emptycomponentlist();
    N:=1
    for(i in 1:N)
    {
        cl.addcomponent(flux=[1.0,0,0,0], ra='0h7m0.0', dec='-42d00m00s',freq=Freq);
        cl.setfreq(i, 1400, 'MHz');
    }
    cl.setspectrum(1:1, 'spectral index', -0.8)
    f:=spaste(holderdir,'/',clname);
    note(spaste('Making componentlist ',f));
    cl.rename(filename=f);
    cl.done();
}
#
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
		      deltafreq='50.0MHz', freqresolution='50.0MHz', 
		      nchannels=1, stokes='RR RL LR LL');
    
    note('Simulating scaled ATCA');
    posatca := dm.observatory('ATCA');

#  Define ATCA xNTD array with 30 antennas

   xx := [-1398.518311, -2799.947754, -43.786434, -1252.077026, 2197.975342, -2422.707520, 3586.145508, 1012.639587, -2161.428467, -1074.882935, 3769.756104, 360.050232, -2489.192871, -1158.198242, -400.231628, -2931.127686, -975.114929, -2974.646484, 237.993591, -360.298035, 2746.886963, 1342.838989, 2092.018066, -624.790771, 3048.720459, -666.824524, 71.983940, 770.071899, -538.815735, 2862.588867]

   yy := [-121.947021, 852.765686, 265.848907, 2375.637451, 2126.479248, 1123.350830, 844.697083, -3248.580566, -2382.272949, -3590.418213, 336.745850, -3556.010498, -1293.422974, 941.583923, 420.135803, 643.004700, -654.646118, -43.957832, 1082.475098, -183.253159, 1995.818237, 2669.032959, -3323.141357, -1419.005981, -791.578369, 822.521667, 3144.392090, -105.612885, -1600.316528, -2682.874512]

   zz:= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := 30
    diam := 0.0 * [1:num_dishes] + Diameter;
    mysim.setconfig(telescopename='ATCA', 
		    x=xx, y=yy, z=zz,
		    dishdiameter=diam, 
		    mount='alt-az', antname='ATCA',
		    coordsystem='local', 
		    referencelocation=posatca);

    dir0    := dm.direction('j2000',  RA, Dec);
    mysim.setfield(sourcename='test_image', 
		   sourcedirection=dir0)

    ref_time := dm.epoch('iat', '2001/01/01');
    mysim.settimes(integrationtime='6s', usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

    starttime:=-2880.0;
    scanlength:=5760.0

    scan:=1;
    while(starttime<2880) {
      mysim.observe('test_image', 'SKA',
		    starttime=spaste(starttime, 's'),
		    stoptime=spaste(starttime+scanlength,'s'));
      dm.doframe(ref_time);
      dm.doframe(posatca);
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
shell('rm -rf TEST_XNTD*.MS mymodel.cl')
print '*** calling mkcomps ***'
mkcomps('mymodel.cl')
print '*** calling simms ***'
simms('TEST_XNTD_30_960.MS','mymodel.cl', ,noise='0.0Jy');
