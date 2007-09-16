include 'autoflag.g'

infile:=0;
# clipping threshold
limm:=1e8;
# uv clip limit
limuv:=1;


### parse args
for( a in argv )
{
  print 'arg: ',a;
  if( a =~ s/ms=// )
    infile:= a;
  else if( a =~ s/minuv=// )
    limuv:=as_integer(a);
  else if( a =~ s/minclip=// )
    limm:=as_float(a);
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
}

print spaste("Postprocessing:::",infile);

### split
include 'ms.g'
include 'os.g'
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



af:=autoflag(newms)
af.setdata()
cliprec:=[=]
cliprec[1] := [expr='ABS XX',min=1e-6,max=limm]
cliprec[2] := [expr='ABS YY',min=1e-6,max=limm]
cliprec[3] := [expr='ABS XY',min=1e-6,max=limm]
cliprec[4] := [expr='ABS YX',min=1e-6,max=limm]
cliprec[5] := [expr='UVD',min=limuv]
af.setselect(clip=cliprec)
af.run()
af.done()

## median flag
af:=autoflag(newms)
af.setdata()
af.settimemed(thr=6,hw=5, expr='ABS XX')
af.settimemed(thr=6,hw=5, expr='ABS XY')
af.settimemed(thr=6,hw=5, expr='ABS YX')
af.settimemed(thr=6,hw=5, expr='ABS YY')
af.run()
af.done()

## special flags, depenging on the measurement set
af:=autoflag(newms)
af.setdata()
af.setselect(ant=1)
af.setselect(ant=2)
af.run()
af.done()




## open with imager
include 'imager.g'
ii:=imager(newms);
ii.done()


print spaste("Done Postprocessing:::",infile);
exit
