# glish/aips++ script to create images from a Measuerement Set
# for both observed, corrected and predicted data.
# Last Edit: 2006.03.28


## Functions ##############################################################
func view_img(img_name){
    # View Image
    include 'image.g'
    img     := image(img_name)
    img.view();
}

func cont_sub(img_name){
    # Subtracts Continuum and saves img_name.line/cont
    include 'image.g'
    line_dat:= paste(img_name, '.line',sep='')
    cont_dat:= paste(img_name, '.cont',sep='')
    fit_ordr:= 0;
    im      := image(img_name)
    im      := im.subimage(region=drm.quarter()) # Speed Things Up
    axes_len:= im.shape()
    margin  := 5              # First/Last channels not used
    end_chan:= axes_len[4]-margin;
    im_csub := im.continuumsub(
            outline  = line_dat,
            outcont  = cont_dat,
            channels = [margin:end_chan],
            overwrite= T,
            fitorder = fit_ordr);
}

func browse(img_name){
    # Browses Through Image
    t       :=table(img_name)      # to make a table tool.
    t.browse()                     # to invoke the browse function.
    #t.close()                     # when finished, close the tool
}

func get_info(img_name){
    # Get Image Info
    im      := image(img_name)
    axes    := im.coordsys().axiscoordinatetypes()
    axes_len:= im.shape()
    im.summary(summ)
    print summ.refpix
    print summ.shape
}

func make_img(img_name, num_px_x, num_px_y, num_chan){
    # Make Image
    include 'imager.g'
    include 'image.g'
    
    cell_x  := 4.0
    cell_y  := 4.0
    
    # Make observed, corrected, predicted Images
    dir     := paste(img_name, '.IM/',sep='')
    shell('mkdir ',dir)
    im_obs  := paste(dir, 'OBS.image',sep='')
    im_cor  := paste(dir, 'COR.image',sep='')
    im_prd  := paste(dir, 'PRD.image',sep='')
    fits_obs:= paste(dir, 'OBS.fits', sep='')
    fits_cor:= paste(dir, 'COR.fits', sep='')
    fits_prd:= paste(dir, 'PRD.fits', sep='')
    
    im      := imager(filename=img_name);
    ok      := im.setdata(mode="channel" , nchan=num_chan);
    ok      := im.setimage(nx=num_px_x, ny=num_px_y, 
            cellx=[value=cell_x, unit="arcsec" ],
            celly=[value=cell_y, unit="arcsec" ], 
            nchan=num_chan, stokes="I" , doshift=F, mode="channel"); 
    ok      := im.makeimage(type="observed",  image=im_obs);
    ok      := im.makeimage(type="corrected", image=im_cor);
    ok      := im.makeimage(type="predicted", image=im_prd);
}            




## MAIN PROGRAM ###########################################################
if (len(argv)<=2){
    print ""; 
    print "glish makeImage.g MS_FILE [imsize] [channels]"; 
    print ""
    exit
} else {
    # Input
    imsize  := 256
    channels:= 1
    if (len(argv)>=4){ imsize  :=as_integer(argv[4]) }
    if (len(argv)>=5){ channels:=as_integer(argv[5]) }

    # Create Images
    make_img(argv[3], imsize, imsize, channels);

    # View Images
    #obs_img := paste(argv[3],".IM/OBS.image" , sep='')
    #view_img(obs_img);
}











###########################################################################
###########################################################################
#reg     := drm.box([10,10],[30,40],[5,5])
#reg     := drm.box([1,1,1,1],[512,512,1,50])
#reg     := drm.box([-0.2,-0.2], [0.2, 0.2], frac=T, absrel='relref')
#im_sub  := im.subimage(outfile='Some name', region=reg)
# Adding Noise
#                                  mean   variance
#im.addnoise(type='normal', pars=[0.001, 0.001], zero=T)
# Create Fits
#obs.tofits(fits_obs);
#cor.tofits(fits_cor);

