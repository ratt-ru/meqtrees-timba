# create, clean, and display image
# using a MS with 16 channels
mkimage:=function(msname)
{
    include 'imager.g';
    include 'measures.g';
    myimager := imager(msname)
    cellsize := '0.4arcsec'
    imsize := 1024
    myimager.setimage(stokes='I',fieldid=1, spwid=1, mode='channel', 
        nchan=16,start=1,step=1, cellx=cellsize, celly=cellsize, 
        nx=imsize, ny=imsize)
    restored_image := 'image.restored'
    model_image := 'image.clean'
    residual_image := 'image.residual'
    myimager.clean(algorithm='clark', niter=10000, gain=0.3, threshold='1mJy',
                  image=restored_image, model=model_image,
                  residual=residual_image)
    include 'image.g'
    myimage := image(restored_image)
    myimage.tofits('image_16chan.fits')
    myimage.view()
}

# to do a run ...
# first delete old MS, test images, etc
shell('rm -rf image.res* image.clean image_16chan.fits')
# now do processing
mkimage('TEST_CLAR_27-480.MS')
