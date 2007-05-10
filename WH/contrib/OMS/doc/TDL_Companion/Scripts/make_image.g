include 'imager.g'
include 'viewer.g'

# default arguments
imagetype:="observed"
msname := "demo.MS"
mode := "mfs";
weighting := "natural";
stokes := "I";
select := "";
npix := 256;
cell := '1arcsec';

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
  else if( a =~ s/mode=// )
    mode := a;
  else if( a =~ s/weight=// )
    weighting := a;
  else if( a =~ s/stokes=// )
    stokes := a;
  else if( a =~ s/npix=// )
    npix := as_integer(a);
  else if( a =~ s/cell=// )
    cell := a;
  else if( a =~ s/msselect=// )
    select := a;
}
print "MS name is ",msname; 

# setup the imager
myimager:=imager(msname)
myimager.setdata(mode='channel',fieldid=1, spwid=1,
             nchan=32,
             start=1,
             step=1,
             msselect=select,
             async=F);

if( mode == 'mfs' )
  myimager.setimage(nx=npix,ny=npix,cellx=cell,celly=cell,
    stokes=stokes,mode=mode,
    fieldid=1,spwid=1,
    nchan=1);
else
  myimager.setimage(nx=npix,ny=npix,cellx=cell,celly=cell,
    stokes=stokes,mode=mode,
    fieldid=1,spwid=1,
    nchan=32,start=1,step=1);

myimager.weight(weighting); 
  
myimager.setoptions(cache=100000000);


# generate an output image name
imgname := msname
imgname =~ s/\..*//;
imgname := spaste(imgname,".",imagetype,"-",stokes,"-",mode);
imgfile := spaste(imgname,".img");

# make the image
myimager.makeimage(type=imagetype,image=imgfile,async=F);


myimager.done()

# convert to FITS
im := image(imgfile);
fitsname := spaste(imgname,'.fits');
im.tofits(fitsname,overwrite=T);
im.done();

print "\n\n--------- wrote FITS image: ",fitsname," ---------\n";

# run Karma
shell(spaste('rm -fr ',imgfile));
shell(spaste('kvis ',fitsname));
exit
