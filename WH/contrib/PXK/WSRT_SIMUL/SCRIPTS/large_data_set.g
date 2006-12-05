
pragma include once

func copy_column(ms='', colfrom='', colto='') { 
    include 'table.g'
    t            := table(ms, readonly=F); 
    chunksize    := 100.0e+6; # Bytes 
    elem_per_row := prod(shape(t.getcell(colfrom,1))); 
    nrows        := floor(chunksize/elem_per_row/8/2); 
    totalrows    := t.nrows(); 

    start        := 1;
    while(start <= totalrows) { 
        print start,'of', totalrows; 
        if(totalrows - start + 1 < nrows) { 
            nrows := totalrows - start + 1; 
        } 
        dcol := t.getcol(colfrom, start, nrows); 
        t.putcol(colto, dcol, start, nrows); 
        start := start+ nrows; 
    } 
    
    t.done(); 
} 