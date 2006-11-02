# script written by imagerwizard.g
include 'imager.g'
include 'viewer.g'
include 'measures.g'
shell('rm -rf xntd.fits xntd_corrected.img')
dir1:=dm.direction('J2000', '00h7m00', '-44d30m00')
myimager:=imager("TEST_XNTD_30_960.MS" )
myimager.setdata(mode='channel',fieldid=1, spwid=1,
             nchan=1,
             start=1,
             step=1,async=F);

myimager.setimage(nx=4096,ny=4096,cellx='1.5arcsec',celly='1.5arcsec', 
  stokes='I',fieldid=1, spwid=1,   
  mode='channel',
  nchan=1,start=1,step=1, doshift=T,phasecenter=dir1)
  
myimager.setoptions(cache=100000000);

imgfile := "xntd_corrected.img";
myimager.makeimage(type="corrected",image=imgfile,async=F);

myimager.done()

im := image(imgfile);
im.tofits('xntd.fits');
im.view();

# plot
# dv.gui()
