include 'imager.g';

pixels := 1024;
pixel_size := '4.0arcsec';

imgr := imager('3C343.MS');
imgr.setdata(mode='channel',nchan=16,start=25,step=1);

imgr.setimage(nx=pixels, ny=pixels, cellx=pixel_size, celly=pixel_size,stokes='I',mode='channel',nchan=16,start=25,step=1);
imgr.weight('uniform');
imgr.makeimage(type='corrected',image='343subtracted.img');
#imgr.clean(algorithm='Clark', niter=1000,threshold='1mJy', displayprogress=T, model='343cleanmodel.img',image='343clean.img');
imgr.done();
exit;
