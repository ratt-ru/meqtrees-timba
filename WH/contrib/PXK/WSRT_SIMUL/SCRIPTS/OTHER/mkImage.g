include 'imager.g'
include 'image.g'
im  :=imager(filename="/home/mevius/LOFAR/Timba/PyApps/test/A963.MS" );
ok:=im.setimage(nx=1024, ny=1024, cellx='4arcsec', 
        celly='4arcsec', nchan=50, stokes='I' , doshift=F, 
	mode='channel'); 
#ok:=im.setdata(mode="channel" , nchan=50);
ok:=im.setdata(mode="channel" , nchan=50,msselect="ANTENNA1 IN [1,2,3,4,5,6,7,8,9,12,13,14] && ANTENNA2 IN [1,2,3,4,5,6,7,8,9,12,13,14]");
#ok:= im.makeimage(type='observed',image='observed');
ok:= im.makeimage(type="corrected", image="corrected");


cor := image("corrected");
ok := cor.continuumsub(outline="corr.sub", fitorder=0);
#obs := image("observed");
#ok := obs.continuumsub(outline="obs.sub", fitorder=0);

#obss:=image('obs.sub')
cors:=image('corr.sub')

cor.tofits("corrected.fits");
#obs.tofits("observed.fits");
cors.tofits("corrected.sub.fits");
#obss.tofits("observed.sub.fits");

