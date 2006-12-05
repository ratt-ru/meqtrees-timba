# aips++/glish script to view an image created from a MS


## Functions ##############################################################
func view_img(img_name){
    include 'image.g'
    img     := image(img_name)
    img.view();
}

func cont_sub(img_name, fit_ordr){
    # Subtracts Continuum and saves img_name.line/cont
    include 'image.g'
    line_dat:= paste(img_name, '.line',sep='')
    cont_dat:= paste(img_name, '.cont',sep='')
    im      := image(img_name)
    #im      := im.subimage(region=drm.quarter()) # Speed Things Up
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
    print('Browsing MS....');
    t       :=table(img_name)      # to make a table tool.
    t.browse()                     # to invoke the browse function.
    #t.close()                     # when finished, close the tool
}

func get_info(img_name){
    # Get Info
    im      := image(img_name)
    axes    := im.coordsys().axiscoordinatetypes()
    axes_len:= im.shape()
    im.summary(summ)
    print summ.refpix
    print summ.shape
}




## MAIN PROGRAM ###########################################################
if (len(argv)<=2){
    print ""; print "glish cont_sub.g IMAGE_NAME"; print ""
    exit
} else {
    if (len(argv)==3){ cont_sub(argv[3], 0)}
    else             { cont_sub(argv[3], as_integer(argv[4]))}
    #line_img:= paste(argv[3],".line" , sep='')
    #view_img(line_img);
    exit
}
