include 'imager.g'
include 'viewer.g'

imagetype:="observed"

if( any(argv=='DATA') )
  imagetype:="observed";
if( any(argv=='MODEL_DATA') )
  imagetype:="model";
if( any(argv=='CORRECTED_DATA') )
  imagetype:="corrected";

  

myimager:=imager("TEST_CLAR_27-480.MS")
myimager.setdata(mode='channel',fieldid=1, spwid=1,
             nchan=32,
             start=1,
             step=1,async=F);

myimager.setimage(nx=1024,ny=1024,cellx='0.25arcsec',celly='0.25arcsec', 
  stokes='I',fieldid=1, spwid=1,   
  mode='channel',
  nchan=32,start=1,step=1)
  
myimager.setoptions(cache=100000000);

#myimager.weight(type="uniform" , async=F)
#myimager.filter(type="gaussian", bmaj='300.0arcsec', bmin='200.0arcsec');

#myimager.weight(type="natural" , async=F)
#myimager.uvrange(uvmin=0, uvmax=2050.68817, async=F)

imgname := spaste("clar-",imagetype);
imgfile := spaste(imgname,".img");
myimager.makeimage(type=imagetype,image=imgfile,async=F);

# imgfile := "clar_corrected.img";
# myimager.makeimage(type="corrected",image=imgfile,async=F);

myimager.done()

im := image(imgfile);
im.tofits(spaste(imgname,'.fits'));
im.view();

print "\n\n--------- press Ctrl+D to exit Glish ---------\n";

# plot
# dv.gui()
