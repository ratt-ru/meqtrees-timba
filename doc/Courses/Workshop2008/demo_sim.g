# glish script that uses newsimulator to simulate a 27 station
# SKA located at the VLA site consisting of 250m dishes.

RA0          := '0h7m0.0';
DEC0         := '33d00m00s';
#DEC0         := '50d00m00s';
#DEC0         := '70d00m00s';
Freq         := '800MHz';
Diameter     := 250.0;
holderdir    := './';

mkcomplist:=function(N,ref flux,ref ra,ref dec)
{
    include 'randomnumbers.g';
    FOV:=1.5;
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
    FOV:=15;

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
    FOV:=15;
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
        cl.setfreq(i, 800, 'MHz');
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
		      deltafreq='16.0MHz', freqresolution='16.0MHz', 
		      nchannels=32, stokes='XX XY YX YY');
    
    note('Simulating scaled VLA');
    posvla := dm.observatory('vla');

#  Define SKA 'C' array, == VLA 'C' array of 27 antennas scaled by factor 10 
#  with local coordinates
#  Using every second antenna would give a 14 antenna array, so equals 
#  number of antennas in WSRT array - should be easy to adapt WSRT trees, etc

     xx := [4110.100006,1340.110001,2680.309998,4390.410004,6440.210022,8800.309998,
   11470.10999,14420.41003,17650.41003,-360.7900009,-1210.690002,-2440.789993,
   -4010.190002,-5880.48999,-8040.690002,-10480.48999,-13180.48999,-16130.98999,
   -40.38999987,-110.29,-220.7900009,-370.6899986,-550.3899994,-750.8899994,
   -990.0899963,-1240.690002,-1520.690002]  

#    xx := [4110.100006,2680.309998,6440.210022, 11470.10999,17650.41003,-1210.690002,
# -4010.190002,-8040.690002,-13180.48999, -40.38999987,-220.7900009,-550.3899994,
# -990.0899963,-1520.690002]


     yy :=[30.51999998,-390.8300018,-1020.480003,-1820.149994,-2770.589996,-3870.839996,
   -5120.119995,-6490.76001,-8000.450012,-20.58999991,-590.9099998,-1420.889999,
   -2480.410004,-3740.690002,-5200.599976,-6850,-8670.099976,-10660.42004,770.1500015,
   1560.910004,2870.980011,4570.429993,6600.409973,8940.700012,11580.82996,14510.43005,
   17710.48999]  

#   yy :=[30.51999998,-1020.480003,-2770.589996, -5120.119995,-8000.450012,-590.9099998,
# -2480.410004,-5200.599976,-8670.099976,770.1500015,
# 2870.980011,6600.409973,11580.82996, 17710.48999]  

     zz := [0.25,-0.439999998,-1.46000004,-3.77999997,-5.9000001,-7.28999996,
   -8.48999977,-10.5,-9.56000042,0.25,-0.699999988,-1.79999995,-3.28999996,
   -4.78999996,-6.48999977,-9.17000008,-12.5299997,-15.3699999,1.25999999,
   2.42000008,4.23000002,6.65999985,9.5,12.7700005,16.6800003,21.2299995,
   26.3299999]  

#   zz := [00.25,-10.46000004,-50.9000001, -80.48999977,-90.56000042,-00.699999988,-30.28999996,
# -60.48999977,-120.5299997,10.25999999, 40.23000002,90.5,160.6800003, 260.3299999]  
    
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
    mysim.settimes(integrationtime='300s', usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

    starttime:=-14400.0;
    scanlength:=28800.0
    scan:=1;
    while(starttime<14400) {
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
print '*** deleting previous stuff ***'
shell('rm -rf demo.MS mymodel.cl')
print '*** calling mkcomplist ***'
num_sources := 1
mkcomplist(num_sources,flux,ra,dec);
print '*** calling mkcomps ***'
mkcomps('mymodel.cl',flux,ra,dec);
print '*** calling simms ***'
simms('demo.MS','mymodel.cl');
