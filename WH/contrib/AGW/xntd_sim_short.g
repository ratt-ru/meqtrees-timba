# glish script that uses newsimulator to simulate a 30 station
# xNTD located at the ATCA site consisting of 12m dishes.

RA0          := '0h7m0.0';
DEC0         := '-45d00m00s';
Freq         := '1400MHz';
Diameter     := 12.0;
holderdir    := './';

mkcomplist:=function(N,ref flux,ref ra,ref dec)
{
    include 'randomnumbers.g';
    FOV:=7.5;
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

    val flux:=array(0.0,N);

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
#        cl.addcomponent(flux=[flux[i],0,0,0], ra=rai, dec=deci,freq=Freq);
#       cl.addcomponent(flux=[1.0,0,0,0], ra='0h7m0.0', dec='-42d00m00s',freq=Freq);
        cl.addcomponent(flux=[1.0,0,0,0], ra='0h9m15.184', dec='-44d35m51.116s',freq=Freq);
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
		      nchannels=1, stokes='XX XY YX YY');
    
    note('Simulating scaled ATCA');
    posatca := dm.observatory('ATCA');

#  Define ATCA xNTD array with 30 antennas

   xx := [-1398.518311, -2799.947754, -43.786434, -1252.077026, 2197.975342, -2422.707520, 3586.145508, 1012.639587, -2161.428467, -1074.882935, 3769.756104, 360.050232, -2489.192871, -1158.198242, -400.231628, -2931.127686, -975.114929, -2974.646484, 237.993591, -360.298035, 2746.886963, 1342.838989, 2092.018066, -624.790771, 3048.720459, -666.824524, 71.983940, 770.071899, -538.815735, 2862.588867]
   xx := xx * 0.5

   yy := [-121.947021, 852.765686, 265.848907, 2375.637451, 2126.479248, 1123.350830, 844.697083, -3248.580566, -2382.272949, -3590.418213, 336.745850, -3556.010498, -1293.422974, 941.583923, 420.135803, 643.004700, -654.646118, -43.957832, 1082.475098, -183.253159, 1995.818237, 2669.032959, -3323.141357, -1419.005981, -791.578369, 822.521667, 3144.392090, -105.612885, -1600.316528, -2682.874512]

   yy := yy * 0.5

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
    mysim.settimes(integrationtime='12s', usehourangle=T, referencetime=ref_time);

    mysim.setlimits(shadowlimit=0.001, elevationlimit='8.0deg')
    mysim.setauto(autocorrwt=0.0);

#   starttime:=-16200.0;
    starttime:=-32400.0
    scanlength:= 32400.0
# over-ride for shorter observation
#   starttime:=-2880.0;
#   scanlength:=5760.0

    scan:=1;
#   while(starttime<2880) {
#   while(starttime<16200) {
    while(starttime<0) {
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
print '*** calling mkcomplist ***'
num_sources := 1
mkcomplist(num_sources,flux,ra,dec);
print '*** calling mkcomps ***'
mkcomps('mymodel.cl',flux,ra,dec);
print '*** calling simms ***'
simms('TEST_XNTD_30_960.MS','mymodel.cl', ,noise='0.0Jy');
