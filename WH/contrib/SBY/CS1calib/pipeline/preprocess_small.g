include 'autoflag.g'

infile:=0;
# clipping threshold
limm:=1e5;
# uv clip limit
limuv:=70;


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

}

print spaste("Preprocessing:::",infile);


af:=autoflag(infile)
af.setdata()
cliprec:=[=]
cliprec[1] := [expr='ABS XX',min=1e-6,max=limm]
cliprec[2] := [expr='ABS YY',min=1e-6,max=limm]
cliprec[3] := [expr='ABS XY',min=1e-6,max=limm]
cliprec[4] := [expr='ABS YX',min=1e-6,max=limm]
cliprec[5] := [expr='UVD',min=limuv]
af.setselect(clip=cliprec)
af.run(reset=T)
af.done()

## median flag
af:=autoflag(infile)
af.setdata()
af.settimemed(thr=6,hw=5, expr='ABS XX')
af.settimemed(thr=6,hw=5, expr='ABS XY')
af.settimemed(thr=6,hw=5, expr='ABS YX')
af.settimemed(thr=6,hw=5, expr='ABS YY')
af.run()
af.done()


## special flags, depenging on the measurement set
#af:=autoflag(infile)
#af.setdata()
#af.setselect(ant=2)
#af.setselect(ant=7)
#af.run()
#af.done()
#af:=autoflag(infile)
#af.setdata()
#af.setselect(ant=[1,2,3,4],timerng="2007/12/10/22:11 2007/12/10/23:31")
#af.setselect(ant=[1,2,3,4],timerng="2007/12/11/09:28 2007/12/11/11:35")
#af.setselect(ant=[1,2,3,4],timerng="2007/12/12/06:10 2007/12/12/07:04")
#af.setselect(ant=[1,2,3,4],timerng="2007/12/12/12:49 2007/12/12/14:03")
#af.setselect(ant=[5,6],timerng="2007/12/10/22:03 2007/12/11/11:43")
#af.setselect(ant=[5,6],timerng="2007/12/12/00:24 2007/12/12/13:58")
#af.run()
#af.done()



###################### compress
include 'ms.g'
include 'os.g'
## append new name to middle
newms:=infile;
newms=~s/.MS//g;
newms=~s/.ms//g;
newms:=sprintf("%s_M.MS",newms);
## check if file already exists
if (dos.fileexists(newms)) {
  print sprintf("Error: File  %s already present, quitting\n",newms);
  exit
} else {
mm:=ms(infile,readonly=F)
mm.split(newms,nchan=[4],start=[32],step=[48]);
mm.done()
}

#### re-run median flagger on new MS
af:=autoflag(newms)
af.setdata()
af.settimemed(thr=6,hw=5, expr='ABS XX')
af.settimemed(thr=6,hw=5, expr='ABS XY')
af.settimemed(thr=6,hw=5, expr='ABS YX')
af.settimemed(thr=6,hw=5, expr='ABS YY')
af.run()
af.done()


## open with imager
include 'imager.g'
ii:=imager(newms);
ii.done()


print spaste("Done Preprocessing:::",infile);
exit
