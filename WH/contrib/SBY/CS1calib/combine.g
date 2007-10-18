include 'ms.g'
mm:=ms("L2007_03464_SB11.MS",readonly=F)
mm.split("f1.ms",nchan=[36],start=[32],step=[1],spwids=[1],fieldids=[1])  
mm.done()

include 'table.g'
tt:=table("f1.ms",readonly=F)
tf:=table("f1.ms/SPECTRAL_WINDOW",readonly=F)
data:=tt.getcol("DATA");
chfreq:=tf.getcol("CHAN_FREQ");
flg:=tt.getcol("FLAG")


mscount:=36;
count:=1;
for ( ci in 1:mscount ){
# get the MS
msname:=sprintf("L2007_03464_SB%d_S.MS",ci-1);
print msname;
cm:=table(msname);
ch0:=table(spaste(msname,"/SPECTRAL_WINDOW")).getcol("CHAN_FREQ");
# loop over spectral windows
for ( spw in 1:1 ) {
 selstring:=sprintf("DATA_DESC_ID==%d",spw-1);
 print selstring
cmt:=cm.query(selstring,sortlist="TIME",columns="CORRECTED_DATA,FLAG");
#cmt.browse()
data[,count,]:=cmt.getcol("CORRECTED_DATA");
flg[,count,]:=cmt.getcol("FLAG");
print count;
print spw;
print ch0::shape
print chfreq::shape
chfreq[count,1]:=ch0[,spw];
cmt.close()
count:=count+1;
}
cm.close()

}

tf.putcol("CHAN_FREQ",chfreq);
tt.putcol("DATA",data);
tt.putcol("FLAG",flg);
tf.close()
tt.close()



exit
