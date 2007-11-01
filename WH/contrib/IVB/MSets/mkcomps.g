# glish script to generate a component list for the MS simulator


RA0          := '0h7m0.0';
DEC0         := '33d00m00s';
Freq         := '59MHz';
holderdir    := '~/data/MSets/';
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
print '*** deleting previous stuff ***'
comm :=spaste('rm -rf ',modelname)
shell(comm)
print '*** calling mkcomplist ***'
num_sources := 1
mkcomplist(num_sources,flux,ra,dec);
print '*** calling mkcomps ***'
mkcomps(modelname,flux,ra,dec);
exit
