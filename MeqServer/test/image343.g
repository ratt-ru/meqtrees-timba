include 'imager.g';

pixels := 2048;
pixel_size := '4.0arcsec';

nchan := 56;#6;
start := 5;#30;
step  := 1;

imgr := imager('3C343.MS');
imgr.setdata(mode='channel',nchan=nchan,start=start, step=step);

imgr.setimage(nx=pixels, ny=pixels, cellx=pixel_size, celly=pixel_size,stokes='I',mode='channel',nchan=nchan,start=start,step=step);
imgr.weight('radial');
imgr.setoptions(padding=1.5);
imgr.makeimage(type='observed',image='343subtracted.img');
#imgr.clean(algorithm='clark', niter=5000,threshold='1mJy', displayprogress=T, model="343model.img",image='343clean.img');


#imgr.setimage(nx=pixels, ny=pixels, cellx=pixel_size, celly=pixel_size,stokes='I',mode='mfs',nchan=1,start=start,step=step);
#imgr.clean(algorithm='clark', niter=5000,threshold='1mJy', displayprogress=T, model="343mfsmodel.img",image='343mfsclean.img');

imgr.done();
exit;
