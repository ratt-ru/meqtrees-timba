# Create Image
include 'mosaicwizard.g';
myimager:=imager(filename="/.automount/halley/root/data/users/kemper/WORK/TIMBA/PXK/A963/A963.MS" , compress=F, host='', forcenewserver=T);
ok:=myimager.summary(); # Gives nchan and stuff
ok:=myimager.setdata(mode="channel" , nchan=50, start=1, step=1, mstart=[value=0.0, unit="km/s" ], mstep=[value=0.0, unit="km/s" ], spwid=1, fieldid=1, msselect='');
ok:=myimager.setimage(nx=512, ny=512, cellx=[value=4.0, unit="arcsec" ], celly=[value=4.0, unit="arcsec" ], stokes="IV" , doshift=F, phasecenter=[type="direction" , refer="J2000" , m1=[value=1.57079633, unit="rad" ], m0=[unit="rad" , value=0.0]], shiftx=[value=0.0, unit="arcsec" ], shifty=[value=0.0, unit="arcsec" ], mode="mfs" , nchan=50, start=1, step=1, mstart=[value=0.0, unit="km/s" ], mstep=[value=0.0, unit="km/s" ], spwid=1, fieldid=1, facets=1, distance=[value=0.0, unit="m" ]);
ok:=myimager.makeimage(type="observed"  , image="observed"  , compleximage='');
ok:=myimager.makeimage(type="corrected" , image="corrected" , compleximage='');
ok:=myimager.makeimage(type="psf"       , image="psf"       , compleximage='');
# View Image
include 'viewer.g';
myviewer:=viewer(title="viewer" , deleteatexit=T);
ok:=myviewer.gui(datamanager=T, displaypanel=T);
