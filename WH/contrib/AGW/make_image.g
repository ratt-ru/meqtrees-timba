# glish script to make simple image from TEST_CLAR.MS
# create, clean, and display image
mkimage:=function(msname)
{
    include 'imager.g';
    myimager := imager(msname)
    cellsize := '0.4arcsec'
    imsize := 1024
    myimager.setdata(mode="channel" , nchan=1, start=1, step=1,
                   spwid=1, fieldid=1);
    myimager.setimage(mode="channel", nchan=1, start=1, step=1,cellx=cellsize, celly=cellsize, nx=imsize, ny=imsize)
    restored_image := 'test_skaim.restored'
    model_image := 'test_skaim.clean'
    residual_image := 'test_skaim.residual'
    print 'calling clean'
    myimager.clean(image=restored_image, model=model_image,
                  residual=residual_image)

    include 'image.g'
    print 'calling image'
    myimage := image(restored_image)
    myimage.tofits('test_ska_image.fits')
    myimage.view()
}

print '*** deleting previous stuff ***'
shell('rm -rf test_skaim*')
# to do a run ...
print '*** calling mkimage ***'
mkimage('TEST_CLAR.MS')
print '*** finished clarsim ***'
