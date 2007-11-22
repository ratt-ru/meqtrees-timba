# glish script to simulate the LOFAR core at WSRT location

# The main input parameters
# Phase center
RA0          := '23h13m0.0';
DEC0         := '59d54m00s';

# Frequency and BW
Frequency    := 60 #Central frequency in MHz
Freq_unit    := 'MHz'
BW_digit     := 2  #Total bandwith in MHz
BW_unit      := 'MHz'
n_chan       := 1

#Dishes (equivalent collecting area for LOFAR)
NN	         := 24
Diameter     := 50.0;

# Time settings for the observations
t_int	     := '120s'# integration time per scan (NB this is a string!)
t_obs        := 2800  # total observing time in seconds

# Basename for file and spectral window
basename     := 'GSM_LOcore'
# Where the MS goes
holderdir    := '/data/bemmel/MSets/';

# Derived settings
# Frequency
Freq_digit   := Frequency-Bandwidth/2
Freq         := spaste(Freq_digit,Freq_unit)
BW	     := spaste(BW_digit,BW_unit)
# Central frequency (need to calculate this from BW and Freq)
# Start and end time
t_start      := -t_obs/2
t_end        := t_obs/2
# Some derived names
specname     := spaste(basename,NN)
msoutname    := spaste(specname,"_",Frequency,"_",BW,"_",t_obs,"_",t_int,".MS")

## LOFAR core ENU coordinates (X=north, Y=east, Z=up)
# for all 24 stations 
# select first 18 stations for the 18-core? --> doesnt work!
# to change 24 --> 18 uncomment the LOFAR 24 and comment the LOFAR 18

# LOFAR 24 station core
if ( NN == 24){
    xx:= [-32.0000, 83.3300, 33.0300, -107.1400, -143.4700, -25.7500, 
          -213.8900, -339.3000, 304.8700, -576.9000, -673.8900, 874.6200, 
          -121.9600, 108.6200, 311.5400, 810.4300, -768.1000, 722.8700, 
          -51.8900, -269.8000, 722.8700, -956.6300, 233.2900, -298.1000]
    yy:= [-175.0000, -205.9000, -74.8600, -82.2100, -217.7900, -294.2400, 
          126.1500, -255.7200, -955.0400, 729.7300, -469.1800, -428.1700, 
          -1211.7200, 230.4900, -479.0400, 28.3900, 129.6000, 660.9600, 
          -426.5100, -126.3700, 660.9600, -281.7200, -297.5100, 1070.2700]
    zz:= [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
          0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
          0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]
        } else { if ( NN == 18) 
            # LOFAR 18 station core
          xx:= [-32.0000, 83.3300, 33.0300, -107.1400, -143.4700, -25.7500, 
               -213.8900, -339.3000, 304.8700, -576.9000, -673.8900, 874.6200, 
                -121.9600, 108.6200, 311.5400, 810.4300, -768.1000, 722.8700]
          yy:= [-175.0000, -205.9000, -74.8600, -82.2100, -217.7900, -294.2400, 
                126.1500, -255.7200, -955.0400, 729.7300, -469.1800, -428.1700, 
                -1211.7200, 230.4900, -479.0400, 28.3900, 129.6000, 660.9600] 
          zz:= [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
                0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 
                0.0000, 0.0000]
        }

    
#-----------------------------------------------------------------------
modelname    := 'newmodel.cl'
#------------------------------------------------------------------------

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
mkcomps:=function(clname=modelname,flux,dRA,dDEC)
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
    
    mysim.setspwindow(spwname=specname, freq=freq,
		      deltafreq=BW, freqresolution=BW, 
		      nchannels=n_chan, stokes='XX XY YX YY');
    
    note('Simulating LOFAR');
    posarray := dm.observatory('wsrt');

# the following number needs to equal the number of elements in each of
# the xx,yy,zz above
    num_dishes := NN
    diam := 0.0 * [1:num_dishes] + Diameter;
    mysim.setconfig(telescopename='LOFAR', 
		    x=xx, y=yy, z=zz,
		    dishdiameter=diam, 
		    mount='alt-az', antname='LOFAR',
		    coordsystem='local', 
		    referencelocation=posarray);

    dir0    := dm.direction('j2000',  RA, Dec);
    ref_time := dm.epoch('iat', '2001/04/01');
    mysim.setfield(sourcename='test_image', 
		   sourcedirection=dir0)

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
      dm.doframe(posarray);
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

#print '*** deleting previous model ***'
#comm :=spaste('rm -rf ',modelname)
#shell(comm)
#print '*** calling mkcomplist ***'
#num_sources := 1
#mkcomplist(num_sources,flux,ra,dec);
#print '*** calling mkcomps ***'
#mkcomps(modelname,flux,ra,dec);
# first delete old MS, test images, etc
print '*** deleting previous MS ***'
comm :=spaste('rm -rf ',msoutname)
shell(comm)
print '*** calling simms ***'
simms(msoutname,modelname);
print 'Written new MS named ',msoutname,' in ',holderdir
exit
