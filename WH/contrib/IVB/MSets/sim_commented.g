# glish script that uses newsimulator to simulate the VLSS layout
# which is VLA B-array, including the VLSS observational settings
# The script uses some hardcoded information for the VLA

# first set the coordinates of the phase center
RA0          := '0h7m0.0';
DEC0         := '33d00m00s';
# start frequency of observations
# combined with bandwith this gives a central frequency of 74.0 MHz
Freq         := '73.25MHz';
# dish diameter
Diameter     := 25.0;
# directory to which the MS should be written
holderdir    := './';
msoutname    := 'ska_test.MS'

#-----------------------------------------------------------------------
# First we need to generate a mock source component, this is required by the simulator
mkcomplist:=function(N,ref flux,ref ra,ref dec)
{
    include 'randomnumbers.g';
    FOV:=15.0;
    r:=randomnumbers();

    r.reseed(10120322231);

    val ra:=array(' ',N);
    val dec:=array(' ',N);
    src:=r.uniform(-FOV,FOV,N);
    for(i in 1:N)
	val dec[i]:=spaste(as_string(src[i]),'arcmin');
    
    src:=r.uniform(-FOV,FOV,N);
    for(i in 1:N)
	val ra[i]:=spaste(as_string(src[i]),'arcmin');

    r.done();

    val flux:=array(1.0,N);

#     val flux:=1;
#     val ra[1]:=spaste('1.5arcmin');
#     val dec[1]:=spaste('1.5arcmin');

}

mk1complist:=function(N,ref flux, ref ra, ref dec)
{
    include 'randomnumbers.g';
    FOV:=150;

    N:=1;
    val ra:=array(' ',N);
    val dec:=array(' ',N);
    
#     val ra[1]:=spaste(as_string(0),'arcmin');
#     val dec[1]:=spaste(as_string(0),'arcmin');
    val ra[1]:=spaste(as_string(0),'arcmin');
    val dec[1]:=spaste(as_string(0),'7arcmin');
    val flux:=array(200E-3,N);
}

mk2complist:=function(N,ref flux,ref ra,ref dec)
{
    include 'randomnumbers.g';
    FOV:=150;
    M:=4*N;
    val ra:=array(' ',M);
    val dec:=array(' ',M);

    doff:=FOV/(N);

    for(i in 1:(2*N))
    {
	val dec[i]:=spaste(as_string((i-N)*doff),'arcmin');
	val ra[i]:=spaste(as_string(0),'arcmin');
    }
    for(i in ((2*N+1):(M)))
    {
	K:=i-M+N;
	print K;
	val dec[i]:=spaste(as_string(0),'arcmin');
	val ra[i]:=spaste(as_string(K*doff),'arcmin');
    }

    val flux:=array(200E-3,M);

#     val flux:=1;
#     val ra[1]:=spaste('1.5arcmin');
#     val dec[1]:=spaste('1.5arcmin');

}
#
#-----------------------------------------------------------------------
#
mkcomps:=function(clname='model.cl',flux,dRA,dDEC)
{
    include 'componentlist.g';
    local f;
    cl:=emptycomponentlist();
    N:=len(dRA);
    refRA:=dq.unit(RA0);
    refDec:=dq.unit(DEC0);
    for(i in 1:N)
    {
	ra := dq.add(refRA,dRA[i]);
	dec:= dq.add(refDec,dDEC[i]);
	rai:=dq.form.long(ra);
	deci:=dq.form.lat(dec);
        ra_demo := dq.convert(ra, 'rad')
        dec_demo := dq.convert(dec, 'rad')
        print 'source ra dec ', i, ' ', rai, ' ', deci
        print 'source ra dec ', i, ' ', ra_demo, ' ', dec_demo
        cl.addcomponent(flux=[flux[i],0,0,0], ra=rai, dec=deci,freq=Freq);
        cl.setfreq(i, 74, 'MHz');
    }
    cl.setspectrum(1:1, 'spectral index', -0.8)
    f:=spaste(holderdir,'/',clname);
    note(spaste('Making componentlist ',f));
    cl.rename(filename=f);
    cl.done();
}
#
#-----------------------------------------------------------------------

# Here starts the AIPS++ routine
#
simms:=function(msname,clname,freq=Freq,noise='0.0Jy',dovp=F,setoffsets=F,
		      RA=RA0,Dec=DEC0)
{
    include 'newsimulator.g';

    simclname:= spaste(holderdir, '/',clname);
    simmsname:= spaste(holderdir, '/',msname);
    
    
    note('Create the empty measurementset');
    
    mysim := newsimulator(msname);
    
# HERE you can set deltafreq and frequency resolution
    mysim.setspwindow(spwname='SKA', freq=freq,
		      deltafreq='1.5MHz', freqresolution='1.5MHz', 
		      nchannels=1, stokes='XX XY YX YY');
    
    note('Simulating VLSS');
# HERE you define which is the default observatory, it sets the global coordinates
    posvla := dm.observatory('vla');

# HERE come the antenna positions in local coordinates
#
## vla -- B array
#
      xx:=[-2629.09,35.6424,560.138,1005.46,-2091.42,114.458,1534.60,306.203,-1660.44,
    1316.47,46.9401,1253.27,2000.10,733.392,-1174.29,-801.383,998.680,-74.7845,
    -489.258,1640.07,377.029,152.779,499.857,765.251,-3217.56,-243.585,229.494]

      yy:=[-410.674,133.658,2113.24,-2643.00,-326.600,438.692,5793.91,-804.578,
    -259.404,-3443.31,-122.026,4733.62,-5299.78,-1932.98,-183.339,-124.993,3764.32,
    -11.7564,-76.3202,-4329.94,1441.00,-401.255,-1317.99,2889.45,-502.651,-38.0320,879.595]

      zz:=[3885.63,-51.0618,-810.675,-1472.17,3089.43,-169.460,-2223.47,-448.058,
    2454.47,-1913.51,-67.5977,-1816.88,-2962.86,-1078.09,1734.24,1182.14,-1443.43,
    111.617,721.546,-2416.68,-556.107,-223.398,-735.197,-1108.87,4756.15,360.062,-339.846]


# the following number needs to equal the number of elements in each of the xx,yy,zz above
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
# HERE you can set the integration time
    mysim.settimes(integrationtime='120s', usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

# HERE you can set the observing time in seconds, I always observe through the meridian
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

# HERE the script is called and run
#
# if you are testing this saves diskspace: first delete old MS, test images, etc
# print '*** deleting previous stuff ***'
# shell('rm -rf ',msoutname)
#
# I have 'mymodel.cl' in my directory, so no need to call mkcomplist
# for the first run of simms you need to uncomment the following 5 lines
#print '*** calling mkcomplist ***'
#num_sources := 1
#mkcomplist(num_sources,flux,ra,dec);
#print '*** calling mkcomps ***'
#mkcomps('mymodel.cl',flux,ra,dec);
#
# Finally call the simulator
print '*** calling simms ***'
simms(msoutname,'mymodel.cl');
exit
# This should do it
