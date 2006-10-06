include 'imager.g'
include 'viewer.g'

# default arguments
imagetype:="observed"
msname := "demo.MS"
mode := "mfs";
weighting := "briggs";
stokes := "I";

# parse command line
for( a in argv )
{
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
}
print "MS name is ",msname; 

# setup the imager
myimager:=imager(msname)
myimager.setdata(mode='channel',fieldid=1, spwid=1,
             nchan=32,
             start=1,
             step=1,async=F);

myimager.setimage(nx=512,ny=512,cellx='0.5arcsec',celly='0.5arcsec', 
  stokes=stokes,mode=mode,
  fieldid=1, spwid=1,   
  nchan=32,start=1,step=1)
  
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

print "\n\n--------- wrote AIPS++ image: ",imgfile;
print "\n\n--------- wrote FITS image: ",fitsname," ---------\n";

# run Karma
shell(spaste('kvis ',fitsname));
exit
