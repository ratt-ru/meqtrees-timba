# glish/aips++ script to create corrupted image
# Last Edit: 2006.04.04

pragma include once


func print_Options(obj){
    opts  := obj.getoptions();
    print field_names(opts);
}


func make_corrupted_img_1chan(file, im_size, chan){
    include 'mosaicwizard.g';
    include 'viewer.g';
    include 'image.g';
    
    # Input
    dir     := paste(file, '.IM/',   sep='')
    shell('mkdir ', dir)
    file_imI:= paste(dir,  'image', sep='')
    file_fts:= paste(dir,  'fits',  sep='')

    cell_x  := 4.0
    cell_y  := 4.0

    # Make Image From Corrected Data Stokes IQUV 
    myimager:= imager(filename=file , compress=F, host='', forcenewserver=T)
    myimager.setdata(mode="channel" , nchan=1, start=chan, step=1);
    myimager.setimage(nx=im_size, ny=im_size, 
        cellx=[value=cell_x, unit="arcsec" ],  
        celly=[value=cell_y, unit="arcsec" ], stokes="IQUV" , doshift=F, 
        mode="mfs" , nchan=1, start=1, step=1);
    myimager.weight(type="uniform" , robust=0.0, npixels=im_size*2,mosaic=F)
    #myimager.clean(algorithm='mfclark', niter=1000, model='mosaic')
    myimager.makeimage(type="corrected" , image=file_imI);

    
    # View Image 
    mdp   := dv.newdisplaypanel(width=800);
    mdd1  := dv.loaddata(file_imI, 'raster'); mdp.register(mdd1);
    #mdd2 := dv.loaddata(file_imQ, 'raster'); mdp.register(mdd2);
    mdd1.setoptions([colormap='Greyscale 1']);
    mdd1.setoptions([axislabelswitch=T])
    mdd1.setoptions([titletext=file_imI, titletextcolor="green"])
    # Test mdd1.setoptions([histoequalisation=T])
    # Test mdd1.setoptions([minmaxhist=T])
    # Test mdd1.setoptions([datamin=0.95 datamax])
    mdp.zoom(3.0);
    #print_Options(mdd1)

    # Show All Four Stokes Parameters
    cm := mdp.canvasmanager(); 
    cm.setoptions([nxpanels=4]);
    # Test cm.setoptions([leftmarginspacepg=0]);

    # Save Image
    #myimage.tofits(file_fts)
    mdp.canvasprintmanager().writeps('image.ps', dpi=300)
}





## MAIN PROGRAM ###################################################
if (len(argv)<=2){
    print "";
    print "glish make_view_save.g MS_FILE [imsize] [startchannel]";
    print ""
    exit
} else {
    # Input
    imsize  := 2048
    channel := 30
    if (len(argv)>=4){ imsize  := as_integer(argv[4]) }
    if (len(argv)>=5){ channel := as_integer(argv[5]) }
    
    # Create Images
    print "Making image of size [", imsize, "] using channel [", channel, "]"
    make_corrupted_img_1chan(argv[3], imsize, channel)    
}


