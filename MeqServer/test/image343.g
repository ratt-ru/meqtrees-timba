include 'imager.g';

pixels := 2048;
pixel_size := '4.0arcsec';

nchan := 8;#6;
start := 26;#30;
step  := 2;

imgr := imager('3C343.MS');
imgr.setdata(mode='channel',nchan=nchan,start=start, step=step);

imgr.setimage(nx=pixels, ny=pixels, cellx=pixel_size, celly=pixel_size,stokes='I',mode='channel',nchan=nchan,start=start,step=step);
imgr.weight('radial');
imgr.setoptions(padding=1.5);
imgr.makeimage(type='corrected',image='343subtracted16.img');
imgr.clean(algorithm='clark', niter=1000,threshold='1mJy', displayprogress=F, model="343model.img",image='343clean.img');


imgr.setimage(nx=pixels, ny=pixels, cellx=pixel_size, celly=pixel_size,stokes='I',mode='mfs',nchan=1,start=start,step=step);
imgr.clean(algorithm='clark', niter=1000,threshold='1mJy', displayprogress=F, model="343mfsmodel.img",image='343mfsclean.img');

imgr.done();
exit;
