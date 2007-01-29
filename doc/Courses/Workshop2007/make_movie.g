include 'imager.g'
include 'image.g'

# default arguments
imagetype:="observed"
msname := "demo.MS"
weighting := "uniform";
stokes := "I";
select := "";
npix := 256;
cellsize := '1arcsec';
channel := 1

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
}
print "MS name is ",msname; 
# generate an output image name
imgname0 := msname
imgname0 =~ s/\..*//;
shell('rm -f *-slice*fits');

for( i in (0:95))
{
  msselect := sprintf('TIME/(24*3600) <= MJD(31dec2000/20:37:32)+(%d*300/(24*3600)) AND TIME/(24*3600) >= MJD(31dec2000/20:37:30)+(%d*300/(24*3600))',i,i);
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
}

# make karma cube
kcube := spaste(imgname0,"-movie.kf");

shell(spaste('images2karma *-slice*fits ',kcube));
shell('rm -f *-slice*fits');
shell(spaste('kvis ',kcube));

exit
