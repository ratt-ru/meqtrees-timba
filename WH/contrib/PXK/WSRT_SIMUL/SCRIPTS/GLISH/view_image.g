# glish/aips++ script to create corrupted image
# glish make_image.g image_file
lastedit := "2006.09.21"

pragma include once


func print_Options(obj){
    opts  := obj.getoptions();
    print field_names(opts);
}



func view_image(file_im, size, zoom, dpi, 
		hist_min=0.0, hist_max=0.0,
		 bar_min=0.0,  bar_max=0.0, 
		powrcycl=0.0,      nxy=2){
    include 'mosaicwizard.g';
    # file_im := "FILES_MS/WSRT_MOD1.MS.IM/image"
    # size     = 512
    # zoom     = 2.0
    # dpi      = 100
    # bar_min  =-0.1
    # bar_max  = 0.1
    # powrcycl = 0.0
    # hist_min = 0.10      # min abs value multiplier
    # hist_max = 0.05      # max abs value multiplier

    print "--- Viewing Image"
    mdp   := dv.newdisplaypanel(width=800, height=600);

    # Show All Four Stokes Parameters
    mdp.setoptions([nxpanels=nxy])
    mdp.setoptions([nypanels=nxy])

    # load data
    mdd1  := dv.loaddata(file_im,  'raster'); mdp.register(mdd1);
    #mdd2 := dv.loaddata(file_im2, 'raster'); mdp.register(mdd2);

    # Set options
    mdd1.setoptions([colormap='Greyscale 1']);
    mdd1.setoptions([axislabelswitch=T])

    if (hist_min!=hist_max){
    	R     := mdd1.getoptions().minmaxhist.default
    	mdd1.setoptions([minmaxhist=[R[1]*hist_min, R[2]*mist_max]])
    }

    if (bar_min!=bar_max){
    	mdd1.setoptions([datamin=bar_min, datamax=bar_max])
    }
    mdd1.setoptions([powercycles=powrcycl, resample='bilinear']);
    mdd1.setoptions([labelcharsize=0.8, plotoutline=F, ticklength=2.0])
    
    #mdd1.setoptions([titletext=file_im])
    #str_size:= paste(size, 'x', size, sep=' ')
    #mdd1.setoptions([titletext=str_size])
    mdd1.setoptions([wedge=T, wedgelabelcharsize=0.8])


    cm := mdp.canvasmanager();
    if (nxy!=1){
        cm.setoptions([bottommarginspacepg=3, topmarginspacepg=1]);
        cm.setoptions([leftmarginspacepg=8, rightmarginspacepg=2]);
    }

    # Save Image    #myimage.tofits(file_fts)
    save    := paste(file_im,  '/image.ps',        sep='')
    savezoom:= paste(file_im,  '/image.zoom.ps',   sep='')
    mdp.canvasprintmanager().writeps(save,     dpi=dpi)
    mdp.zoom(zoom);
    mdp.canvasprintmanager().writeps(savezoom, dpi=dpi)

    # Colors
    #mdd1.setoptions([titletextcolor="green"])
    #mdd1.setoptions([xaxistextcolor='grey', yaxistextcolor='grey'])
    #mdd1.setoptions([wedgeaxistextcolor='grey'])
}





## MAIN PROGRAM ###################################################
if (len(argv)<=2){
    print "";
    print "glish view_image.g file"
    print "...... zoom=2.0, dpi=100, hist_min=0.10, hist_max=0.05,  ";
    print ".......bar_min=-0.1, bar_max=0.1, powrcycl=0.0           ";
    print ""
    exit
} else {
    # Input
    L := len(argv)
    if (L>=4) {imsize   := as_integer(argv[4]) } else {imsize   := 512}
    if (L>=5) {zoom     := as_double (argv[5]) } else {zoom     := 2.0}
    if (L>=6) {dpi      := as_integer(argv[6]) } else {dpi      := 100}
    if (L>=7) {hist_min := as_double (argv[7]) } else {hist_min := 0.10}
    if (L>=8) {hist_max := as_double (argv[8]) } else {hist_max := 0.05}
    if (L>=9) {bar_min  := as_double (argv[9]) } else {bar_min  :=-0.1}
    if (L>=10){bar_max  := as_double (argv[10])} else {bar_max  := 0.1}
    if (L>=11){powrcycl := as_double (argv[11])} else {powrcycl := 0.0}
    if (L>=12){nxy      := as_integer(argv[12])} else {nxy      := 2}

    # Create Images
    print ""
    print "#########################################################"
    print "# lastedit: ", lastedit
    print "# imsize..: ", imsize
    print "# zoom....: ", zoom
    print "# dpi.....: ", dpi
    print "# hist_min: ", hist_min
    print "# hist_max: ", hist_max
    print "# bar_min.: ", bar_min
    print "# bar_max.: ", bar_max
    print "# powrcycl: ", powrcycl
    print "# nxy.....: ", nxy
    print "#########################################################"
    print ""

    view_image(argv[3], imsize, zoom, dpi, 
		hist_min, hist_max, bar_min, bar_max, powrcycl, nxy)
}


