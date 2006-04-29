include 'imager.g'
include 'viewer.g'

imagetype:="observed"

if( any(argv=='DATA') )
  imagetype:="observed";
if( any(argv=='MODEL_DATA') )
  imagetype:="model";
if( any(argv=='CORRECTED_DATA') )
  imagetype:="corrected";
if( any(argv=='RESIDUAL') )
  imagetype:="residual";

msname := "TEST_CLAR_27-480.MS"
mode := "mfs";

for ( a in argv )
{
  if( a =~ s/ms=// )
    msname := a;
  else if( a =~ s/mode=// )
    mode := a;
}
print "MS name is ",msname; 

myimager:=imager(msname)
myimager.setdata(mode='channel',fieldid=1, spwid=1,
             nchan=32,
             start=1,
             step=1,async=F);

myimager.setimage(nx=1024,ny=1024,cellx='0.25arcsec',celly='0.25arcsec', 
  stokes='I',fieldid=1, spwid=1,   
  mode=mode,
  nchan=32,start=1,step=1)
  
myimager.setoptions(cache=100000000);

#myimager.weight(type="uniform" , async=F)
#myimager.filter(type="gaussian", bmaj='300.0arcsec', bmin='200.0arcsec');

#myimager.weight(type="natural" , async=F)
#myimager.uvrange(uvmin=0, uvmax=2050.68817, async=F)

imgname := msname
imgname =~ s/\..*//;
imgname := spaste(imgname,".",imagetype,"-",mode);
imgfile := spaste(imgname,".img");
myimager.makeimage(type=imagetype,image=imgfile,async=F);

# imgfile := "clar_corrected.img";
# myimager.makeimage(type="corrected",image=imgfile,async=F);

myimager.done()

im := image(imgfile);
fitsname := spaste(imgname,'.fits');
im.tofits(fitsname,overwrite=T);
# im.view();

print "\n\n--------- wrote AIPS++ image: ",imgfile;
print "\n\n--------- wrote FITS image: ",fitsname," ---------\n";

shell(spaste('kvis ',fitsname));
# print "\n\n--------- press Ctrl+D to exit Glish ---------\n";

# plot
# dv.gui()
exit
