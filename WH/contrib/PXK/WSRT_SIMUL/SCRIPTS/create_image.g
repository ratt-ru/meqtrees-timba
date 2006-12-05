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
# default arguments
imagetype   := "observed"
msname      := "F"
mode        := "mfs";
weighting   := "briggs";
stokes      := "I";
select      := "";
npix        := 256;
cell        := '1arcsec';
image_viewer:= 'kvis';
fieldid     := 1;
spwid       := 1;
nchan       := 1;
chanstart   := 1;
chanstep    := 1;
zoom        := 1.0;   # my parameters:
dpi         := 100
hist_min    := 0.10
hist_max    := 0.05
datamin     := -0.1
datamax     := 0.1
powrcycl    := 0.0
nxy         := 2
color       := 0


# parse command line
for( a in argv ){
  print 'arg: ',a;
  if( a =='DATA' )
    imagetype:="observed";
  else if( a =='MODEL_DATA' )
    imagetype:="model";
  else if( a =='CORRECTED_DATA' )
    imagetype:="corrected";
  else if( a =='RESIDUAL' )
    imagetype:="residual";
  else if( a =~ s/ms=// )
    msname := a;
  else if( a =~ s/mode=// )
    mode := a;
  else if( a =~ s/weight=// )
    weighting := a;
  else if( a =~ s/stokes=// )
    stokes := a;
  else if( a =~ s/npix=// )
    npix := as_integer(a);
  else if( a =~ s/cellsize=// )
    cell := a;
  else if( a =~ s/viewer=// )
    image_viewer := a;
  else if( a =~ s/fieldid=// )
    fieldid := as_integer(a);
  else if( a =~ s/spwid=// )
    spwid := as_integer(a);
  else if( a =~ s/nchan=// )
    nchan := as_integer(a);
  else if( a =~ s/chanstart=// )
    chanstart := as_integer(a);
  else if( a =~ s/chanstep=// )
    chanstep := as_integer(a);
  else if( a =~ s/powercycle=// ) # My input parameters:
    powercycle := as_double(a);
  else if( a =~ s/powercycle=// )
    zoom := as_double(a);
  else if( a =~ s/dpi=// )
    dpi := as_integer(a);
  else if( a =~ s/hist_min=// )
    hist_min := as_double(a);
  else if( a =~ s/hist_max=// )
    hist_max := as_double(a);
  else if( a =~ s/datamin=// )
    datamin := as_double(a);
  else if( a =~ s/datamax=// )
    datamax := as_double(a);
  else if( a =~ s/nxy=// )
    nxy := as_integer(a);
  else if( a =~ s/color=// )
    color := as_integer(a);
}


print "imagetype: ", imagetype
print "msname: ", msname   
print "mode: ", mode
print "weighting: ", weighting
print "stokes: ", stokes   
print "select: ", select   
print "npix: ", npix    
print "cell: ", cell    
print "image_viewer: ", image_viewer
print "fieldid: ", fieldid
print "spwid: ", spwid
print "nchan: ", nchan
print "chanstart: ", chanstart
print "chanstep: ", chanstep
print "zoom: ", zoom
print "dpi: ", dpi
print "hist_min: ", hist_min
print "hist_max: ", hist_max
print "datamin: ", datamin
print "datamax: ", datamax
print "powrcycl: ", powrcycl
print "nxy: ", nxy
print "color: ", color





make_corrupted_img(msname, npix, chanstart, nchan, cellsize, zoom, dpi, 
		   hist_min, hist_max, datamin, datamax, powrcycl, nxy,
                   color)
# Clean up aips++ stuff
shell('rm -rf ', '0')
shell('rm -rf ', 'aips++.records.table/')
shell('rm -rf ', 'aips++.inputsv2.table/')
}


