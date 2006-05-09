# script written by imagerwizard.g
include 'imager.g'
include 'viewer.g'
myimager:=imager("TEST_CLAR_27-480.MS" )
myimager.setdata(mode='channel',fieldid=1, spwid=1,
             nchan=32,
             start=1,
             step=1,async=F);

myimager.setimage(nx=1024,ny=1024,cellx='0.25arcsec',celly='0.25arcsec', 
  stokes='I',fieldid=1, spwid=1,   
  mode='mfs',
  nchan=32,start=1,step=1)
  
myimager.setoptions(cache=100000000);

#myimager.weight(type="uniform" , async=F)
#myimager.filter(type="gaussian", bmaj='300.0arcsec', bmin='200.0arcsec');

#myimager.weight(type="natural" , async=F)
#myimager.uvrange(uvmin=0, uvmax=2050.68817, async=F)

#imgfile := "clar_data.img";
#myimager.makeimage(type="observed",image=imgfile,async=F);

imgfile := "clar_corrected.img";
myimager.makeimage(type="corrected",image=imgfile,async=F);

myimager.done()

im := image(imgfile);
im.tofits('clar.fits');
im.view();

# plot
# dv.gui()
