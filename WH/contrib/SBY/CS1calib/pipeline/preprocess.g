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
#af.setselect(ant=15)
#af.run()
#af.done()


## open with imager
include 'imager.g'
ii:=imager(infile);
ii.done()


print spaste("Done Preprocessing:::",infile);
exit
