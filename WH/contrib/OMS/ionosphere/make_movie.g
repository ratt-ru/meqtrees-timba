include 'imager.g'
include 'image.g'

msname := 'demo-sim.MS';
npix := 1024;
# cellsize := '10arcsec'; # full field
cellsize := '1arcsec'; # full field
weight := "uniform";

for( i in (0:95))
{
  msselect := sprintf('TIME/(24*3600) <= MJD(31dec2000/20:37:32)+(%d*300/(24*3600)) AND TIME/(24*3600) >= MJD(31dec2000/20:37:30)+(%d*300/(24*3600))',i,i);
  # setup the imager
  myimager:=imager(msname);
  print msselect;
  myimager.setdata(mode='channel',fieldid=1, spwid=1,
               nchan=1,
               start=1,
               step=1,
               msselect=msselect,
               async=F);

  print select;
  myimager.setimage(nx=npix,ny=npix,cellx=cellsize,celly=cellsize, 
    stokes="I",mode='mfs',
    fieldid=1,spwid=1,
    nchan=1,start=1,step=1);

  myimager.weight(weight); 

  myimager.setoptions(cache=100000000);

  # generate an output image name
  imgname := msname
  imgname =~ s/\..*//;
  imgname := spaste(imgname,"-slice",sprintf("%03d",i));
  imgfile := spaste(imgname,".img");

  # make the image
  myimager.makeimage(type='observed',image=imgfile,async=F);

  # convert to FITS
  im := image(imgfile);
  fitsname := spaste(imgname,'.fits');
  im.tofits(fitsname,overwrite=T);
  im.done();
  shell(spaste('rm -fr ',imgfile));
}
