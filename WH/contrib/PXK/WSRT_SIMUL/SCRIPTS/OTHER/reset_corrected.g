include 'table.g'
vis:= table('A963.MS', readonly=F);
vis.removecols("CORRECTED_DATA");
t:=tablecreatearraycoldesc("CORRECTED_DATA",as_complex(0),2,[2,50]);
vis.addcols(t);
