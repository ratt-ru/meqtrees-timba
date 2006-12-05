#! /bin/bash -f
# glish/aips++ script to make a movie in time of data
#
# History:
#  - 2006.11.30: creation
#  - 2006.12.01: improvements on input handling etc.
#  - 2006.12.02: minor change


pragma include once


function time_movie(msname, imagetype, mode, weight, stokes, 
    npix, cellsize, select){
    # I am not using keyword 'select'

    include 'imager.g'
    include 'image.g'
    include 'table.g'

    # Get time of data
    t        := table(msname)    #t.browse()
    thetime  := t.getcol('TIME')
    TIME0    := thetime[1]
    TIME1    := thetime[shape(thetime)]
    print "[time-range]: ", TIME0, TIME1

    # get number of baselines (!) must be easier way!
    ant1     :=t.getcol('ANTENNA1')
    ant2     :=t.getcol('ANTENNA2')
    autocorr := F
    N        := 0
    for (i in (1:shape(thetime))){
	if (ant1[i] == ant2[i]) { autocorr := T;         }
 	if (ant2[i] >= N)       { N        := ant2[i]+1; }
    }
    print "antennas :", N
    print "autocorr :", autocorr
    baselines:= (N * (N-1))/2
    if (autocorr == T) {baselines:= baselines+N;}
    print "baselines:", baselines

    # get interval and number of timeslots
    interval := t.getcol('INTERVAL') # EXPOSURE??
    timeslots:= shape(thetime)/baselines
    print "interval : ", interval[1]
    print "timeslots: ", timeslots

    t_steps   := timeslots - 1
    for( i in (0:t_steps)){

	print ""
	print ""
	print "_____________________________________________________________"
	print i+1, "/", timeslots
	#lower    := sprintf('MJD(2000/12/31/20:37:30)+(%d*300/(24*3600))', i);
	#upper    := sprintf('MJD(2000/12/31/20:37:32)+(%d*300/(24*3600))', i);
	step     := sprintf('(%d*%f/(24*3600))', i, interval[1]);
	lower    := sprintf('%f + %s', (TIME0  )/(24*3600), step);
	upper    := sprintf('%f + %s', (TIME0+2)/(24*3600), step);
	time     := sprintf('TIME/(24*3600)');
	msselect := sprintf('%s <= %s AND %s >= %s',time, upper, time, lower);
	print msselect;

	# setup the imager
	myimager:=imager(msname);
	myimager.setdata(mode='channel',fieldid=1, spwid=1,
		    nchan=1, start=1,step=1, msselect=msselect,async=F);
	
	myimager.setimage(nx=npix,ny=npix,cellx=cellsize,celly=cellsize, 
	    stokes=stokes,mode=mode,
	    fieldid=1,spwid=1,nchan=1,start=1,step=1);

	myimager.weight(weight); 
	myimager.setoptions(cache=100000000);

	# generate an output image name
	imgname := msname
	imgname =~ s/\..*//;
	imgname := spaste(imgname,"-slice",sprintf("%03d",i));
	imgfile := spaste(imgname,".img");

	# make the image and convert to FITS
	myimager.makeimage(type=imagetype,image=imgfile,async=F);
	im := image(imgfile);
	fitsname := spaste(imgname,'.fits');
	im.tofits(fitsname,overwrite=T);
	im.done();
	shell(spaste('rm -fr ',imgfile));
    }
    print "done..."

    # generate an output base name
    name := msname
    name =~ s/\..*//;
    
    # create single karma file from slices
    shell(spaste('mkdir ', name, '.SLICES', sep=''));
    shell(spaste('mv ', name, '-slice* ', name, '.SLICES', sep=''));
    shell(spaste('images2karma ',name,'.SLICES/', name,'* ',name,'',sep=''));

    # move slices into MS
    shell(spaste('rm -rf ', msname, '/', name, '.SLICES', sep=''));
    shell(spaste('mv ', name, '.SLICES ', msname, sep=''));
    
    # run Karma
    shell(spaste('kvis ',name, '.kf &', sep=''));
    exit
}









## MAIN PROGRAM ###################################################
if (len(argv)<=2){
    print "";
    print "glish time_movie.g file"
    print ""
    exit
} else {

    # default arguments
    msname    := "demo.MS"
    imagetype := "observed"
    mode      := "mfs";
    weighting := "natural";
    stokes    := "I";
    select    := "";
    npix      := 512;
    cell      := '1arcsec';
    select    := ""

    # parse command line
    for( a in argv ){
    print 'arg: ',a;
    if     ( a =~ s/ms=// )         msname   := a;
    else if( a =='DATA' )           imagetype:="observed";
    else if( a =='MODEL_DATA' )	    imagetype:="model";
    else if( a =='CORRECTED_DATA' ) imagetype:="corrected";
    else if( a =='RESIDUAL' )	    imagetype:="residual";
    else if( a =~ s/mode=// )       mode     := a;
    else if( a =~ s/weight=// )     weighting:= a;
    else if( a =~ s/stokes=// )     stokes   := a;
    else if( a =~ s/npix=// )	    npix     := as_integer(a);
    else if( a =~ s/cell=// )       cell     := a;
    else if( a =~ s/msselect=// )   select   := a;
    }
    print "MS name is ",msname; 


    time_movie(msname, imagetype, mode, weighting, stokes, npix, cell, select);
}




