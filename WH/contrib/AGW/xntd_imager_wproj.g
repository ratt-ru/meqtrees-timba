# create, clean, and display image
# we use w-projection correction
mkimage:=function(msname)
{
    include 'imager.g';
    include 'measures.g';
    myimager := imager(msname)
    cellsize := '3arcsec'
    imsize := 2048
    myimager.setimage(stokes='I',fieldid=1, spwid=1, mode='channel', 
        nchan=1,start=1,step=1, cellx=cellsize, celly=cellsize, 
        nx=imsize, ny=imsize)
    myimager.setoptions(ftmachine='wproject', wprojplanes=128)
    restored_image := 'image.restored'
    model_image := 'image.clean'
    residual_image := 'image.residual'
    myimager.clean(algorithm='mfhogbom', niter=2000, gain=0.2, threshold='1mJy',
                  image=restored_image, model=model_image,
                  residual=residual_image)
    include 'image.g'
    myimage := image(restored_image)
    myimage.tofits('xntd.fits')
}

# to do a run ...
# first delete old MS, test images, etc
shell('rm -rf image.res* image.clean xntd.fits')
# now do processing
mkimage('TEST_XNTD_30_960.MS')
