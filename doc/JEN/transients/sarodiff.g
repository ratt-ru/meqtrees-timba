# ../doc/JEN/transients/sarodiff.g  (18 july 2006)

# Glish script to subtract the average of preceding and succeeding uv-samples
# from each uv-sample.



##############################################
include 'table.g'
tt:=table("casa.ms",readonly=F);
## if you want to copy the DATA column to CORRECTED_DATA column
tt.putcol("CORRECTED_DATA",tt.getcol("DATA"));
tt.flush();
## iterate over baselines
visbyants:=tableiterator(tt, "ANTENNA1 ANTENNA2");
visbyants.reset();
while(visbyants.next()) {
 nrows:=visbyants.table().nrows();
 # get columns
 t1:=visbyants.table().query(sortlist="TIME",columns="CORRECTED_DATA");
 vl:=t1.getcol("CORRECTED_DATA");
 # get shape
 npol:=vl::shape[1];
 nchan:=vl::shape[2];
 ntime:=vl::shape[3];
 # form difference
 aa:=vl[1:npol,1:nchan,1:(ntime-2)];
 bb:=vl[1:npol,1:nchan,3:ntime];
 cc:=vl[1:npol,1:nchan,2:(ntime-1)];
 # copy back
 vl[1:npol,1:nchan,2:(ntime-1)]:=cc-(aa+bb)/2;
 # set the first and last values
 vl[1:npol,1:nchan,1]:=vl[1:npol,1:nchan,2];
 vl[1:npol,1:nchan,ntime]:=vl[1:npol,1:nchan,ntime-1];

 #aa:=vl[1:npol,1:nchan,1:(ntime-1)];
 #bb:=vl[1:npol,1:nchan,2:ntime];
 #vl[1:npol,1:nchan,1:(ntime-1)]:=(aa-bb);
 t1.putcol("CORRECTED_DATA",vl);
 t1.flush();
 print "Wrote  baseline: [", visbyants.table().getcell("ANTENNA1", 1),",", visbyants.table().getcell("ANTENNA2", 1), "] polarizations: ", npol,", channels: ", nchan,", samples:", ntime;
}

visbyants.done();
tt.flush();
tt.close();