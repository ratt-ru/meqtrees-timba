include 'table.g';


flag_column_abs := function(msname, column_name, threshold, erase=F)
{
    t := table(msname, readonly=F);

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell(column_name,1)));
    nrows        := floor(chunksize/elem_per_row/8/5);
    totalrows    := t.nrows();

    start := 1;
    limit := threshold*threshold
    while(start <= totalrows) {
        print start,'of', totalrows;

        if(totalrows - start + 1 < nrows) {
            nrows := totalrows - start + 1;
        }

        dcol := t.getcol(column_name, start, nrows);
        
        absdcol := dcol*conj(dcol);
        fcol := absdcol >= limit;
        if(!erase){
            flagcol := t.getcol('FLAG', start,nrows);
            fcol |:= flagcol;
        }
        fplane := fcol[1,,] | fcol[2,,] |fcol[3,,] | fcol[4,,];
        fcol[1,,] := fplane;
        fcol[2,,] := fplane;
        fcol[3,,] := fplane;
        fcol[4,,] := fplane;
        t.putcol('FLAG', fcol,start, nrows);
        start := start+ nrows;
    }

    t.close();
}

