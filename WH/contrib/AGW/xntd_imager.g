# create, clean, and display image of a source as seen by an offaxis
# beam of an XNTD array
mkimage:=function(msname)
{
    include 'imager.g';
    include 'measures.g';
    myimager := imager(msname)
    cellsize := '1.0arcsec'
    imsize := 1024
#   dir1:=dm.direction('J2000', '00h07m00', '-48d00m00')
    myimager.setimage(stokes='I',fieldid=1, spwid=1, mode='channel', 
        nchan=1,start=1,step=1, cellx=cellsize, celly=cellsize, 
        nx=imsize, ny=imsize)
#       nx=imsize, ny=imsize, doshift=T,phasecenter=dir1)
    restored_image := 'image.restored'
    model_image := 'image.clean'
    residual_image := 'image.residual'
    myimager.clean(algorithm='clark', niter=10000, gain=0.3, threshold='1mJy',
                  image=restored_image, model=model_image,
                  residual=residual_image)
    include 'image.g'
    myimage := image(restored_image)
    myimage.tofits('image_xntd.fits')
    myimage.view()
}

# to do a run ...
# first delete old MS, test images, etc
shell('rm -rf image.res* image.clean image_xntd.fits')
# now do processing
mkimage('TEST_XNTD_30_640.MS')
