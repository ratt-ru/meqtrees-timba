include 'imager.g'
include 'viewer.g'
include 'image.g'
include 'os.g'

## default
infile:=0;
fid:=1;
defstartch:=32;
endch:=224;
step:=8;
minspwid:=1;
maxspwid:=1;
limuv:=3400;


### parse args
for( a in argv )
{
  print 'arg: ',a;
  if( a =~ s/ms=// )
    infile:= a;
  else if( a =~ s/minspwid=// )
    minspwid:=as_integer(a);
  else if( a =~ s/maxspwid=// )
    maxspwid:=as_integer(a);
  else if( a =~ s/startch=// )
    defstartch:=as_integer(a);
  else if( a =~ s/endch=// )
    endch:=as_integer(a);
  else if( a =~ s/step=// )
    step:=as_integer(a);
  else if( a =~ s/minuv=// )
    limuv:=as_integer(a);

}

# CygA
#myphasecenter:=dm.direction('J2000', '19h57m42','40d35m54')
# CasA
#myphasecenter:=dm.direction('J2000', '23h23m24','58d48m54')
#transient
#myphasecenter:=dm.direction('J2000', '20h10m00','40d30m00')
#NCP
myphasecenter:=dm.direction('J2000', '00h00m00','90d00m00')


# default
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > %d",fid,limuv)
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > 100 and (TIME/(24*3600) <= MJD(28apr2007/08:49:00)) or TIME/(24*3600) >= MJD(28apr2007/20:29:00)",fid)
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > 100)",fid)
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > 100 and (TIME/(24*3600) <= MJD(19may2007/12:46:00)) or TIME/(24*3600) >= MJD(19may2007/18:02:00)",fid)
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > %d and (TIME/(24*3600) <= MJD(28may2007/16:11:00)) and  TIME/(24*3600) >= MJD(27may2007/19:06:00)",fid,limuv)
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > %d and (TIME/(24*3600) <= MJD(27may2007/15:21:00)) and  TIME/(24*3600) >= MJD(26may2007/19:06:00)",fid,limuv)
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > %d and (( (TIME/(24*3600) >= MJD(24aug2007/14:30:00)) and  (TIME/(24*3600) <= MJD(25aug2007/08:17:00)) ) ) and sqrt(sumsqr(CORRECTED_DATA))/2<15000",fid,limuv)
# HBA 4309
#msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > %d and (( (TIME/(24*3600) >= MJD(07nov2007/16:20:00)) and  (TIME/(24*3600) <= MJD(08nov2007/03:17:00)) ) ) and sqrt(sumsqr(CORRECTED_DATA))/2<15000",fid,limuv)
msstr:=sprintf("FIELD_ID==%d AND sumsqr(UVW[1:2]) > %d and sqrt(sumsqr(CORRECTED_DATA))/2<45000",fid,limuv)


print spaste("Postprocessing:::",infile);

### split
include 'ms.g'
## append new name to middle
newms:=infile;
newms=~s/.MS//g;
newms=~s/.ms//g;
newms:=sprintf("%s_S.MS",newms);
## check if file already exists
if (dos.fileexists(newms)) {
  print sprintf("Error: File  %s already present, quitting\n",newms);
  exit
} else {
mm:=ms(infile,readonly=F)
mm.split(newms,nchan=[1],start=[defstartch],step=[endch-defstartch+1],whichcol='CORRECTED_DATA');
mm.done()
}



spid:=minspwid;
while(spid<=maxspwid) {

startch:=1;
my_img:=sprintf("%s_d%d_%d.img",infile,startch,spid)

myimager:=imager(newms)
myimager.setdata(mode='channel', fieldid=fid, spwid=spid,
             nchan=1,
             start=startch, msselect=msstr,
             step=1, async=F);
#HBA
myimager.setimage(nx=3456, ny=3456, cellx='120arcsec', celly='120arcsec',  stokes='IQUV', phasecenter=myphasecenter, doshift=T, fieldid=fid, spwid=spid, mode='channel', nchan=1, start=startch, step=1)
#LBA
#myimager.setimage(nx=1728, ny=1728, cellx='240arcsec', celly='240arcsec',  stokes='IQUV', phasecenter=myphasecenter, doshift=T, fieldid=fid, spwid=spid, mode='channel', nchan=1, start=startch, step=1)
myimager.setoptions(ftmachine='wproject', wprojplanes=128, padding=1.2 , cache=500000000)
myimager.makeimage(type="corrected",image=my_img,async=False);
myimager.close()
myimager.done()


#### after making images, create mean image
startch:=1;

im:=image(my_img);
fits_img:=sprintf("%s_c1_%d.fits",infile,spid)
im.tofits(fits_img)
im.close()


spid:=spid+1;
}

print spaste("End Postprocessing:::",infile);

## dont call exit here, because we run this async
exit
