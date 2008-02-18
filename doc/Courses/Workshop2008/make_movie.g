include 'imager.g'
include 'image.g'
include 'table.g'

# default arguments
imagetype:="observed"
msname := "demo.MS"
weighting := "uniform";
stokes := "I";
select := "";
npix := 256;
cellsize := '1arcsec';
channel := 1
nframes := 96;
dt := 300;

# parse command line
for( a in argv )
{
  print 'arg: ',a;
  if( a =='DATA' )
    imagetype:="observed";
  else if( a =='MODEL_DATA' )
    imagetype:="model";
  else if( a =='CORRECTED_DATA' )
    imagetype:="corrected";
  else if( a =='RESIDUAL' )
    imagetype:="residual";
  else if( a =~ s/ms=// )
    msname := a;
  else if( a =~ s/channel=// )
    channel := as_integer(a);
  else if( a =~ s/weight=// )
    weighting := a;
  else if( a =~ s/npix=// )
    npix := as_integer(a);
  else if( a =~ s/cell=// )
    cellsize := a;
  else if( a =~ s/nframes=// )
    nframes := as_integer(a);
  else if( a =~ s/dt=// )
    dt := as_integer(a);
}
print "MS name is ",msname; 
# generate an output image name
imgname0 := msname
imgname0 =~ s/\..*//;
shell('rm -f *-slice*fits');

tbl :=table(msname);
tm := tbl.getcol('TIME');
tbl.done();
t0 := tm[1]-1;

for( i in (0:(nframes-1)))
{
#  msselect := sprintf('TIME/(24*3600) <= MJD(31dec2000/20:37:32)+(%d/(24.*3600)) AND TIME/(24.*3600) >= MJD(31dec2000/20:37:30)+(%d/(24.*3600))',i*dt,i*dt);
  msselect := sprintf('TIME >= %.12f AND TIME <= %.12f',t0+i*dt,t0+(i+1)*dt);
  # setup the imager
  myimager:=imager(msname);
  print msselect;
  myimager.setdata(mode='channel',fieldid=1, spwid=1,
               nchan=1,
               start=channel,
               step=1,
               msselect=msselect,
               async=F);

  print select;
  myimager.setimage(nx=npix,ny=npix,cellx=cellsize,celly=cellsize, 
    stokes="I",mode='mfs',
    fieldid=1,spwid=1,
    nchan=1,start=channel,step=1);

  myimager.weight(weighting); 

  myimager.setoptions(cache=100000000);

  # generate an output image name
  imgname := spaste(imgname0,"-slice",sprintf("%03d",i));
  imgfile := spaste(imgname,".img");

  # make the image
  myimager.makeimage(type=imagetype,image=imgfile,async=F);

  # convert to FITS
  im := image(imgfile);
  fitsname := spaste(imgname,'.fits');
  im.tofits(fitsname,overwrite=T);
  im.done();
  shell(spaste('rm -fr ',imgfile));
  myimager.done();
  myimager:=F;
}

# make karma cube
kcube := spaste(imgname0,"-movie.kf");

shell(spaste('images2karma *-slice*fits ',kcube));
shell('rm -f *-slice*fits');
shell(spaste('kvis ',kcube));

exit
