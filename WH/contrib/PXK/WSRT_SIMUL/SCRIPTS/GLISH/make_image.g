#!/usr/bin/env python
# glish/aips++ script to create corrupted image
# glish make_image.g image_file
lastedit := "2006.10.09"

pragma include once


func print_Options(obj){
    opts  := obj.getoptions();
    print field_names(opts);
}



func view_image(file_im, size, zoom, dpi, 
		hist_min=0.0, hist_max=0.0,
		 datamin=0.0,  datamax=0.0, 
		powrcycl=0.0,      nxy=2, 
		color=1){
    include 'mosaicwizard.g';
    # file_im := "FILES_MS/WSRT_MOD1.MS.IM"
    # size     = 512
    # zoom     = 2.0
    # dpi      = 100
    # datamin  =-0.1
    # datamax  = 0.1
    # powrcycl = 0.0
    # hist_min = 0.10      # min abs value multiplier
    # hist_max = 0.05      # max abs value multiplier

    print "--- Viewing Image"
    mdp   := dv.newdisplaypanel(width=800, height=600);
    mdp.setoptions([nxpanels=nxy])    # Show All Four Stokes Parameters
    mdp.setoptions([nypanels=nxy])

    # load data
    dv.hold()
    mdd1  := dv.loaddata(file_im,  'raster');
    mdp.register(mdd1);
    dv.release()

    # Set options
    R     := mdd1.getoptions().minmaxhist.default
    if (hist_min!=hist_max)
        {mdd1.setoptions([minmaxhist=[R[1]*hist_min, R[2]*mist_max]])}

    mdd1.setoptions([powercycles=powrcycl, resample='bilinear']);
    mdd1.setoptions([labelcharsize=0.8, plotoutline=F, ticklength=2.0])
    if (datamin!=datamax)
        {mdd1.setoptions([datamin=datamin, datamax=datamax])}
        

    if (0){
        mdd1.setoptions([titletext=file_im])
        str_size:= paste(size, 'x', size, sep=' ')
        mdd1.setoptions([titletext=str_size])
    }


    # set wedge
    mdd1.setoptions([wedge=T, wedgelabelcharsize=0.8])


    # set margins
    cm := mdp.canvasmanager();
    if (nxy!=1){
        cm.setoptions([bottommarginspacepg=3, topmarginspacepg=1]);
        cm.setoptions([leftmarginspacepg=8, rightmarginspacepg=2]);
    }


    # Set colors and save
    if (color==2){
        D := abs(R[2]*0.6)
        mdd1.setoptions([datamin=-D, datamax=D])
        cm.setoptions([colortablesize=8])
        color_and_save(mdd1, mdp, file_im, 'Misc. 2: Topography',  dpi, 1.0)
        if (zoom!=1.0){
          mdp.zoom(zoom);
          color_and_save(mdd1, mdp, file_im, 'Misc. 2: Topography',  dpi, zoom)
        }
    } else {
        color_and_save(mdd1, mdp, file_im, 'Greyscale 1', dpi, 1.0)
        if (color!=0){
            color_and_save(mdd1, mdp, file_im, 'Rainbow 1',   dpi, 1.0)
            color_and_save(mdd1, mdp, file_im, 'RGB 2',       dpi, 1.0)
        }
        if (zoom!=1.0){
            mdp.zoom(zoom);
            color_and_save(mdd1, mdp, file_im, 'Greyscale 1', dpi, zoom)
            if (color!=0){
                color_and_save(mdd1, mdp, file_im, 'Rainbow 1',   dpi, zoom)
                color_and_save(mdd1, mdp, file_im, 'RGB 2',       dpi, zoom)
            }
        }
    }

}


func color_and_save(mdd1, mdp, file, cmap, dpi, zoom){
    # Set colormap
    mdd1.setoptions([colormap=cmap]);
    mdd1.setoptions([axislabelswitch=T])

    # Save Image
    cmap    =~ s/ /./g      # replace all ' ' by '.' inplace
    base    := paste(file,  '/image.',	sep='')
    ext     := paste(base,  cmap,	sep='')
    if (zoom==1.0){save := paste(ext,   '.ps',	sep='')}
    else          {save := paste(ext,   '.zoom.ps',	sep='')}
    mdp.canvasprintmanager().writeps(save,     dpi=dpi)
}



func make_corrupted_img(file, im_size, start, chans, cell_size, zoom, dpi, 
			hist_min, hist_max, datamin, datamax,
			powrcycl, nxy, color){
    include 'mosaicwizard.g';
    print "--- Making corrupted Image"

    # Input
    file_imI:= paste(file, '.IM',   sep='')
    shell('rm -rf ', file_imI)
    #shell('mkdir ',  file_imI)
    #file_fts:= paste(file_imI,  '/fits',  sep='')

    cell_x  := cell_size
    cell_y  := cell_size  

    # Make Image From Corrected Data Stokes IQUV 
    # 'mfs': single image plane with multiple-frequency
    myimager:= imager(filename=file , compress=F, host='', forcenewserver=T)
    myimager.setdata(
	mode="channel" , 
	nchan=chans, start=start, step=1);
    myimager.setimage(nx=im_size, ny=im_size, 
        cellx=[value=cell_x, unit="arcsec" ],  
        celly=[value=cell_y, unit="arcsec" ], stokes="IQUV" , doshift=F, 
	mode="mfs"       # mfs ignores nchan, start, step
	#mode="channel" , nchan=1, start=start, step=1      # 1 channel
	#mode="channel" , nchan=1, start=start, step=chans  # averaging
        #mode="channel" , nchan=chans, start=start, step=1  # cube (slow!)
	);
    myimager.setoptions(cache=100000000);
    myimager.weight(type="uniform" , robust=0.0, npixels=im_size*2,mosaic=F)
    #myimager.clean(algorithm='mfclark', niter=1000, model='mosaic')
    myimager.makeimage(type="corrected" , image=file_imI);
        
    # View Image 
    view_image(file_imI, im_size, zoom, dpi, hist_min, hist_max,
		datamin, datamax, powrcycl, nxy, color)

}





## MAIN PROGRAM ###################################################
if (len(argv)<=2){
    print "";
    print "glish make_image.g file"
    print "...... imsize=512,start=1,chans=1,cellsize=4.0,zoom=2.0, ";
    print ".......dpi=100, hist_min=0.10, hist_max=0.05,            ";
    print ".......datamin=-0.1, datamax=0.1, powrcycl=0.0           ";
    print ""
    exit
} else {
    # Input
    L := len(argv)
    if (L>=4) {imsize   := as_integer(argv[4]) } else {imsize   := 512}
    if (L>=5) {start    := as_integer(argv[5]) } else {start    := 1}
    if (L>=6) {chans    := as_integer(argv[6]) } else {chans    := 1}
    if (L>=7) {cell_size:= as_double (argv[7]) } else {cell_size:= 4.0}
    if (L>=8) {zoom     := as_double (argv[8]) } else {zoom     := 2.0}
    if (L>=9) {dpi      := as_integer(argv[9]) } else {dpi      := 100}
    if (L>=10){hist_min := as_double (argv[10])} else {hist_min := 0.10}
    if (L>=11){hist_max := as_double (argv[11])} else {hist_max := 0.05}
    if (L>=12){datamin  := as_double (argv[12])} else {datamin  :=-0.1}
    if (L>=13){datamax  := as_double (argv[13])} else {datamax  := 0.1}
    if (L>=14){powrcycl := as_double (argv[14])} else {powrcycl := 0.0}
    if (L>=15){nxy      := as_integer(argv[15])} else {nxy      := 2}
    if (L>=16){color    := as_integer(argv[16])} else {color    := 0}

    # Create Images
    print ""
    print "#########################################################"
    print "# lastedit: ", lastedit
    print "# imsize..: ", imsize
    print "# cellsize: ", cell_size
    print "# startchn: ", start
    print "# endchn:.. ", start+chans-1
    print "# zoom....: ", zoom
    print "# dpi.....: ", dpi
    print "# hist_min: ", hist_min
    print "# hist_max: ", hist_max
    print "# datamin.: ", datamin
    print "# datamax.: ", datamax
    print "# powrcycl: ", powrcycl
    print "# nxy.....: ", nxy
    print "# color...: ", color
    print "#########################################################"
    print ""
    make_corrupted_img(	argv[3], imsize, start, chans, cell_size, zoom, dpi, 
			hist_min, hist_max, datamin, datamax, powrcycl, nxy, 
			color)

    # Clean up aips++ stuff
    shell('rm -rf ', '0')
    shell('rm -rf ', 'aips++.records.table/')
    shell('rm -rf ', 'aips++.inputsv2.table/')
}


