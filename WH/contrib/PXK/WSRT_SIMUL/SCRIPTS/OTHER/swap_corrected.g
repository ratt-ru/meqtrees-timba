include 'table.g'
vis:= table('A963.MS', readonly=F);
t:=vis.getcol("CORRECTED_DATA");
vis.putcol("DATA",t);
