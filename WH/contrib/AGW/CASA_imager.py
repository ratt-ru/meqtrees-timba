# CASA script to create, clean, and display an image.
# Execute this script from within the CASA environment by issuing the
# CASA command: execfile('name_of_script') 

# get rid of old versions of files to be created in this script
import os
os.system('rm -rf image.res* image.clean 3C84_image.fits')

# start using the imager (im) tool
msname = '3C84L.MS'
im.selectvis(vis=msname, field='0319+415')
cellsize = '2arcsec'
imsize = 4096
im.defineimage(stokes='I', mode= 'mfs', cellx=cellsize, celly=cellsize, nx=imsize, ny=imsize)
# we use w-projection correction
im.setoptions(ftmachine='wproject', wprojplanes=64)
restored_image = 'image.restored'
model_image = 'image.clean'
residual_image = 'image.residual'
im.clean(algorithm='clark', niter=3000, gain=0.1, threshold='0.0mJy',
                  image=restored_image, model=model_image,
                  residual=residual_image)

# use the image (ia) tool to get a fits file output
ia.open(restored_image)
ia.tofits('3C84_image.fits')
