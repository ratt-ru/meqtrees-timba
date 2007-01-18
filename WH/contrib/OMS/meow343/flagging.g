include 'autoflag.g';
include 'table.g';
include 'quanta.g';
include 'string-handling.g';
include 'functional.g';

#====================>>>  clearflags  <<<====================

clearflags := function(ms='')
{
    print 'Clear FLAG column of', ms;
    column := 'FLAG';
    fr_column := 'FLAG_ROW';
    t := table(ms, readonly=F);
    if(is_fail(t)) {
        print('clearflags(): failed to open MS');
        return F;
    }
    

    chunksize    := 100.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell(column,1)));
    nrows        := floor(chunksize/elem_per_row/8);

    totalrows := t.nrows();
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        dcol := t.getcol(column, start, nrows);
        rcol := t.getcol(fr_column, start, nrows);
        if(is_fail(dcol)) {
            t.close();
            return F;
        }

        dcol  &:= F;
        rcol  &:= F;

        t.putcol(column, dcol, start, nrows);
        t.putcol(fr_column, rcol, start, nrows);
        start := start + nrows;
    }
    t.done();
    print 'FLAG cleared';
}




flag_IFs := function(msname, ant=[], iflist=[])
{
    flg := autoflag(msname);
    flg.setdata();
    flg.setselect(ant=ant,spwid=iflist);
    flg.run(devfile=F);
    flg.done();
}


equalize_flags := function(msname)
{
    print 'Equalizing flags...';
    t := table(msname,readonly=F);

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell('FLAG',1)));
    nrows        := floor(chunksize/elem_per_row/10);
           
    totalrows :=  t.nrows();
    spwtab := table(t.getkeyword('SPECTRAL_WINDOW'));
    chan_freq := spwtab.getcol('CHAN_FREQ');
    spwtab.close();

    num_chan := shape(chan_freq)[1];
    print 'NUM_CHAN = ', num_chan;
    start := 1;
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
                                                

        flags := t.getcol('FLAG',start, nrows);
        flagplane := flags[1,,]|flags[2,,]|flags[3,,]|flags[4,,];
        flag_row := array(F, nrows);
        for(i in 1:nrows){
           flag_row[i] := sum(as_integer(flagplane[,i])) > 0.75*num_chan;
           if(flag_row[i] == T){
               flagplane[,i] |:= T;
           }
        }
        flags[1,,] := flagplane;
        flags[2,,] := flagplane;
        flags[3,,] := flagplane;
        flags[4,,] := flagplane;
    
        t.putcol('FLAG', flags,start,nrows);
        t.putcol('FLAG_ROW', flag_row,start,nrows);
   
        start := start + nrows;
    }
    t.done();
    print 'Done.'
    return T;
}


flag_clip := function(msname,data_column='DATA',threshold=[1.0,1.0,1.0,1.0])
{
# Threshold = [xx, xy, yx, yy]
    print 'Clipping ', msname,data_column;
    print 'Threshold = ', threshold;

    flag_column := 'FLAG';
    
    t := table(msname, readonly=F);
    if(is_fail(t)) {
        print(spaste('flag_clip(): failed to open MS ',msname));
        return F;
    }
    

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell(data_column,1)));
    nrows        := floor(chunksize/elem_per_row/8/5);

    totalrows := t.nrows();
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        flags := t.getcol(flag_column, start, nrows);
        dcol  := t.getcol(data_column, start, nrows);
        if(is_fail(dcol)) {
            print 'Failed to open DATA column';
            t.close();
            return F;
        }

        flagscol := flags;
        for(i in 1:4){
            flagscol[i,,] |:= (abs(dcol)[i,,] > threshold[i]);
        }
        t.putcol(flag_column, flagscol, start, nrows);
        start := start + nrows;
    }
    t.done();
    print 'Done.';
    return T;
}


flag_residuals := function(msname, threshold=1.0, minuvw=-1.0, maxuvw=100e+9)
{
    print 'Flagging on residuals of ', msname;
    flag_column := 'FLAG';
    data_column := 'CORRECTED_DATA';
    model_column := 'MODEL_DATA';
    
    t := table(msname, readonly=F);
    if(is_fail(t)) {
        print(spaste('flag_residuals(): failed to open MS ',msname));
        return F;
    }
    
    spwtab    := table(t.getkeyword('SPECTRAL_WINDOW'));
    chan_freq := spwtab.getcol('CHAN_FREQ');
    spwtab.close();
    
    num_chan := shape(chan_freq)[1];

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell(data_column,1)));
    nrows        := floor(chunksize/elem_per_row/8/6);

    totalrows := t.nrows();
    start     := 1;
    C := 299792458.0;

    print spaste('****  threshold = ', threshold);
    print spaste('****  minuvw    = ', minuvw   );
    print spaste('****  maxuvw    = ', maxuvw   );
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        dcol := t.getcol(data_column, start, nrows);
        mcol := t.getcol(model_column, start, nrows);
        flags := t.getcol(flag_column, start, nrows);
        uvw_m := t.getcol('UVW', start, nrows);
        uvwdist_m := sqrt(uvw_m[1,]*uvw_m[1,] +
                       uvw_m[2,]*uvw_m[2,]);#UV distance
        spwid := t.getcol('DATA_DESC_ID', start, nrows);
        
        if(is_fail(dcol) || is_fail(mcol)) {
            print 'Failed to open either CORRECTED_DATA or MODEL_DATA column';
            t.close();
            return F;
        }

        uvwmaskplane := flags[1,,] & F;
        for(i in 1:nrows){
            uvwlambda := (uvwdist_m[i]*chan_freq[,spwid[i]+1]/C);
            uvwmaskplane[,i] := (uvwlambda > minuvw) & (uvwlambda < maxuvw);
        }
        uvwmask := flags & F;
        uvwmask[1,,]:= uvwmaskplane;
        uvwmask[2,,]:= uvwmaskplane;
        uvwmask[3,,]:= uvwmaskplane;
        uvwmask[4,,]:= uvwmaskplane;
        extraflags := ((abs(dcol-mcol) > threshold) & uvwmask);
        flagscol := flags | extraflags;

        t.putcol(flag_column, flagscol, start, nrows);
        start := start + nrows;
    }
    t.done();
    equalize_flags(msname);
    print 'Done.';
    return T;
}


flag_QUV := function(msname, threshold=1.0)
{
    print 'Flagging on CORRECTED_DATA QUV of ', msname;
    flag_column := 'FLAG';
    data_column := 'CORRECTED_DATA';
    model_column := 'MODEL_DATA';
    
    t := table(msname, readonly=F);
    if(is_fail(t)) {
        print(spaste('flag_residuals(): failed to open MS ',msname));
        return F;
    }
    

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell(data_column,1)));
    nrows        := floor(chunksize/elem_per_row/8/3);

    totalrows := t.nrows();
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        dcol := t.getcol(data_column, start, nrows);
        flags := t.getcol(flag_column, start, nrows);
        if(is_fail(dcol)) {
            print 'Failed to open either CORRECTED_DATA column';
            t.close();
            return F;
        }

        Q := (dcol[1,,]-dcol[4,,])/2.0;
        U := (dcol[2,,]+dcol[3,,])/2.0;
        V := (dcol[3,,]-dcol[2,,])/2.0i;
        flagplane := (abs(Q) > threshold) | (abs(U) > threshold) | (abs(V) > threshold);
        flagscol := flags;
        flagscol[1,,] |:= flagplane;
        flagscol[2,,] |:= flagplane;
        flagscol[3,,] |:= flagplane;
        flagscol[4,,] |:= flagplane;
                    

        t.putcol(flag_column, flagscol, start, nrows);
        start := start + nrows;
    }
    t.done();
    equalize_flags(msname);
    print 'Done.';
    return T;
}



flag_QUVXYYX := function(msname, threshold=1.0)
{
    print 'Flagging on CORRECTED_DATA XY and YX of ', msname;
    flag_column := 'FLAG';
    data_column := 'CORRECTED_DATA';
    model_column := 'MODEL_DATA';
    
    t := table(msname, readonly=F);
    if(is_fail(t)) {
        print(spaste('flag_QUVXYYX(): failed to open MS ',msname));
        return F;
    }
    

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell(data_column,1)));
    nrows        := floor(chunksize/elem_per_row/8/3);

    totalrows := t.nrows();
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        dcol := t.getcol(data_column, start, nrows);
        flags := t.getcol(flag_column, start, nrows);
        if(is_fail(dcol)) {
            print 'Failed to open either CORRECTED_DATA column';
            t.close();
            return F;
        }

        Q := (dcol[1,,]-dcol[4,,])/2.0;
        U := (dcol[2,,]+dcol[3,,])/2.0;
        V := (dcol[3,,]-dcol[2,,])/2.0i;
        xy := dcol[2,,];
        yx := dcol[3,,];
        flagplane := (abs(Q) > threshold*1.5) | (abs(xy) > threshold) | (abs(yx) > threshold) | (abs(U) > threshold) | (abs(V) > threshold);
        flagscol := flags;
        flagscol[1,,] |:= flagplane;
        flagscol[2,,] |:= flagplane;
        flagscol[3,,] |:= flagplane;
        flagscol[4,,] |:= flagplane;
                    

        t.putcol(flag_column, flagscol, start, nrows);
        start := start + nrows;
    }
    t.done();
    equalize_flags(msname);
    print 'Done.';
    return T;

}



# Flags data with uv distance less than  "min"
# The timerng argument is an array of times
# If the length is larger than 0, only data with
# timerng[1] <= mjd <= timerng[2] || timerng[3] <= mjd <= timerng[4] || ....
# are eligible for flagging
flag_uvdistance := function(msname, min=0.0, timerng="")
{
    #min is in lambda
    C := 299792458.0;
    print 'Flagging on uv distance: ', msname;
    print 'min distance = ',min;
    flag_column := 'FLAG';
    
    t := table(msname, readonly=F);
    if(is_fail(t)) {
        print(spaste('flag_uvdistance(): failed to open MS ',msname));
        return F;
    }
    spwtab    := table(t.getkeyword('SPECTRAL_WINDOW'));
    chan_freq := spwtab.getcol('CHAN_FREQ');
    spwtab.close();
    
    num_chan := shape(chan_freq)[1];

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell('FLAG',2)));
    nrows        := floor(chunksize/elem_per_row/8);

    # Make selection
    global system;
    pp := system.print.precision;
    system.print.precision := 12;
    sSelect:= ' ( TIME > 0 ) ';
    fFirst := T;
    if(len(timerng) > 0){
        for(i in 1:(len(timerng)/2)){
            a := dq.convert(timerng[2*i-1]).value;
            b := dq.convert(timerng[2*i]).value;
            if(fFirst){
                sSelect := '';
                fFirst := F;
            }else{
                sSelect := spaste(sSelect, ' || ');
            }
            sSelect := spaste(sSelect, ' ( TIME_CENTROID >= ', a, ' && TIME_CENTROID <= ', b,' ) ' );
        }
    }
    system.print.precision := pp;
    print 'Selecting ', sSelect;
    sel := t.query(sSelect);


    totalrows := sel.nrows();
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        uvw_m := sel.getcol('UVW', start, nrows);
        spwid := sel.getcol('DATA_DESC_ID', start, nrows);
        flags := sel.getcol(flag_column, start, nrows);
        time_centroid := sel.getcol('TIME_CENTROID', start, nrows);
        if(is_fail(uvw_m)) {
            print 'Failed to open UVW column';
            print uvw_m;
            sel.close();
            t.close();
            return F;
        }

        uvwdist_m := sqrt(uvw_m[1,]*uvw_m[1,] +
                       uvw_m[2,]*uvw_m[2,]);#UV distance
        flagscol := array(F,4,num_chan, nrows);
        flagscol |:= flags;
        newflags := array(F, num_chan, nrows);
        for(i in 1:nrows){
            newflags[,i] := ((uvwdist_m[i]*chan_freq[,spwid[i]+1]/C) < min);
        }
        flagscol[1,,] |:= newflags;
        flagscol[2,,] |:= newflags;
        flagscol[3,,] |:= newflags;
        flagscol[4,,] |:= newflags;

        sel.putcol(flag_column, flagscol, start, nrows);
        start := start + nrows;
    }
    sel.done();
    t.done();
    print 'Done.';
    return T;
}





# threshold function takes one parameter, the uv distance in wavelengths,
# and returns a threshold in whatever units the MS is currently in.
flag_threshold_function := function(msname, column, threshold_function_xyyx=F, threshold_function_xxyy=F)
{
    #min is in lambda
    C := 299792458.0;
    print 'Flagging on threshold XY/YX (function) ', msname;
    flag_column := 'FLAG';
    
    t := table(msname, readonly=F);
    if(is_fail(t)) {
        print(spaste('flag_xyyx_gauss_offset(): failed to open MS ',msname));
        return F;
    }
    spwtab    := table(t.getkeyword('SPECTRAL_WINDOW'));
    chan_freq := spwtab.getcol('CHAN_FREQ');
    spwtab.close();
    
    num_chan := shape(chan_freq)[1];

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell('FLAG',2)));
    nrows        := floor(chunksize/elem_per_row/32);

    totalrows := t.nrows();
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        uvw_m := t.getcol('UVW',          start, nrows);
        spwid := t.getcol('DATA_DESC_ID', start, nrows);
        flags := t.getcol(flag_column,    start, nrows);
        data  := t.getcol(column,         start, nrows);
        time_centroid := t.getcol('TIME_CENTROID', start, nrows);
        if(is_fail(uvw_m)) {
            print 'Failed to open UVW column';
            print uvw_m;
            t.close();
            return F;
        }

        uvwdist_m := sqrt(uvw_m[1,]*uvw_m[1,] +
                       uvw_m[2,]*uvw_m[2,]);#UV distance
        flagscol := array(F,4,num_chan, nrows);
        flagscol |:= flags;
        newflags := array(F, num_chan, nrows);
        for(i in 1:nrows){
            uvw_dist_lambda := (uvwdist_m[i]*chan_freq[,spwid[i]+1]/C);
            if(is_function(threshold_function_xyyx)){
                threshold := threshold_function_xyyx(uvw_dist_lambda);
                newflags[,i] |:= (abs(data[2,,i]) >= threshold) | (abs(data[3,,i]) >= threshold);
            }
            if(is_function(threshold_function_xxyy)){
                threshold := threshold_function_xxyy(uvw_dist_lambda);
                newflags[,i] |:= (abs(data[1,,i]) >= threshold) | (abs(data[4,,i]) >= threshold);
            }
        }
        flagscol[1,,] |:= newflags;
        flagscol[2,,] |:= newflags;
        flagscol[3,,] |:= newflags;
        flagscol[4,,] |:= newflags;

        t.putcol(flag_column, flagscol, start, nrows);
        start := start + nrows;
    }
    t.done();
    print 'Done.';
    return T;
}



flagselect_query := function(antids=[], spwids=[], timerng="")
{
    query:='';
    sep  := ' && ';
    query := append_if_nonempty(query, query_antennae(antids), sep=sep);
    query := append_if_nonempty(query, query_spwids(spwids)  , sep=sep);
    query := append_if_nonempty(query, query_timerng(timerng), sep=sep);

    return query;
}




flagselect := function(msname, antids=[], spwids=[],timerng="",channels=[])
{
    t := table(msname, readonly=F);
    if(is_fail(t)){
        print t;
        return F;
    }

    query := flagselect_query(antids=antids, spwids=spwids, timerng=timerng);
    sel := t.query(query);
    
    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(sel.getcell('FLAG',2)));
    nrows        := floor(chunksize/elem_per_row/32);

    totalrows := sel.nrows();
    print '';
    print '******************************************************************************';
    print 'Selection', msname, 'ant=',antids, 'spw=',spwids, 'timerng=', timerng, 'channels=', channels;
    print totalrows,'rows in selection';
    print '******************************************************************************';
    print '';
    start     := 1;
 
    while( start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        flag_col     := sel.getcol('FLAG', start, nrows);
        flag_row_col := sel.getcol('FLAG_ROW', start, nrows);
        if(is_boolean(channels) || len(channels) == 0){
            flag_col |:= T;
            flag_row_col |:= T;
        }else{
            flag_col[,channels[1]:channels[2],] |:= T;
        }
        sel.putcol('FLAG'    , flag_col, start, nrows);
        sel.putcol('FLAG_ROW', flag_row_col, start, nrows);
        start +:= nrows;
    }

    sel.done();
        
    return T;
}




distance_between_antennae := function(positions, ant1, ant2)
{
    return as_integer(0.5 + sqrt(sum((positions[,ant1] - positions[,ant2])^2)));
}



baseline_rms := function(msname, column='DATA')
{
    t := table(msname);
    ant_tab := table(t.getkeyword('ANTENNA'));
    positions := ant_tab.getcol('POSITION');
    ant_tab.done();
    
    result_list := map_ms(function(table_object, start, nrows){
        rms    := array(0.0, 4, 3000);
        counts := array(0  , 4, 3000);
        data_col_name  := column;
        if(column == 'RESIDUAL_DATA'){
            data_col_name := 'CORRECTED_DATA';
        }
        ant1_col := table_object.getcol('ANTENNA1'   , start, nrows)+1;
        ant2_col := table_object.getcol('ANTENNA2'   , start, nrows)+1;
        flag_col := table_object.getcol('FLAG'       , start, nrows);
        data_col := table_object.getcol(data_col_name, start, nrows);
        if(column == 'RESIDUAL_DATA'){
            data_col -:= table_object.getcol('MODEL_DATA', start, nrows);
        }
        for(i in 1:nrows){
            ix           := distance_between_antennae(positions, ant1_col[i], ant2_col[i]);
            if(ix > 0){
                valid_points :=  1.0 - as_float(flag_col[,,i]);
                sum_squares  := array(0.0,4);
                weights      := array(0.0,4);
                for(pol in 1:4){
                    sum_squares[pol] := sum(abs(data_col[pol,,i]*valid_points[pol,])^2);
                    weights    [pol] := sum(valid_points[pol,]);
                }
                rms   [,ix] +:= sum_squares;
                counts[,ix] +:= weights;
            }
        }
        result := [=];
        result.rms    := rms;
        result.counts := counts;
        return result;
    }, t);

    result := reduce(function(current,next_one){
        result.rms    := current.rms    + next_one.rms;
        result.counts := current.counts + next_one.counts;
        return result;
    }, result_list);
    

    counts := 1-as_integer(result.counts>0)+result.counts;
    return sqrt(result.rms/counts);
}


flag_rms := function(msname, column='DATA', factors=[5,5,5,5])
{
    rms_from_baseline_m := baseline_rms(msname);
    for(i in 1:4){
        rms_from_baseline_m[i,] *:= factors[i];
    }

    t := table(msname, readonly=F);
    ant_tab := table(t.getkeyword('ANTENNA'));
    positions := ant_tab.getcol('POSITION');
    ant_tab.done();
    
    result_list := map_ms(function(table_object, start, nrows){
        data_col_name  := column;
        if(column == 'RESIDUAL_DATA'){
            data_col_name := 'CORRECTED_DATA';
        }
        ant1_col := table_object.getcol('ANTENNA1', start, nrows)+1;
        ant2_col := table_object.getcol('ANTENNA2', start, nrows)+1;
        flag_col := table_object.getcol('FLAG'    , start, nrows);
        data_col := table_object.getcol(data_col_name, start, nrows);
        if(column == 'RESIDUAL_DATA'){
            data_col -:= table_object.getcol('MODEL_DATA', start, nrows);
        }
        newflags := flag_col[1,,]&F;
        for(row in 1:nrows){
            baseline_m := distance_between_antennae(positions, ant1_col[row], ant2_col[row]);
            if(baseline_m == 0){
                newflags[,row] |:= T;
            }else{
                threshold  := rms_from_baseline_m[,baseline_m];
                for(pol in 1:4){
                    newflags[,row] |:= (abs(data_col[pol,,row]) > threshold[pol]);
                }
            }
        }
        for(pol in 1:4){
            flag_col[pol,,] |:= newflags;
        }
        table_object.putcol('FLAG', flag_col, start, nrows);
        return T;
    },t);
    t.done();
    
    return reduce(function(a,b){
        if(is_fail(a) || is_fail(b)){
            print a;
            print b;
            return F;
        }
        return a && b;
    }, result_list);
}



flagreport := function(msname)
{
    t       := table(msname);
    
    ddt     := table(t.getkeyword('DATA_DESCRIPTION'));
    num_spw := ddt.nrows();
    ddt.done();
    
    spwt      := table(t.getkeyword('SPECTRAL_WINDOW'));
    chan_freq := spwt.getcol('CHAN_FREQ');
    num_chan  := spwt.getcol('NUM_CHAN');
    spwt.done();
    
    anttab := table(t.getkeyword('ANTENNA'));
    num_ant := anttab.nrows();
    anttab.done();
    
    flags_per_spw := array(0.0, num_spw);
    weights       := array(0.0, num_spw);
    
    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(t.getcell('FLAG',1)));
    nrows        := floor(chunksize/elem_per_row/8);
    start := 1
    totalrows := t.nrows();
    
    while(start <= totalrows){
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
                                               
        flags := as_integer(t.getcol('FLAG',start,nrows)[1,,]);
        ddid  := t.getcol('DATA_DESC_ID',start,nrows);
        for( i in 1:nrows){
            spwid := ddid[i]+1;
            flags_per_spw[spwid] +:= as_double(sum(flags[,i]))/num_chan[spwid];
            weights[spwid] +:= 1;
        }
        start := start + nrows;
    }
    t.done();
    flags_per_spw /:= weights;
    for(i  in  1:num_spw){
        if(weights[i] == 0){
            flags_per_spw[i] := 0;
        }
    }

    print '*******************************************************';
    print spaste('| ',paste(flags_per_spw, sep=' | '),'| ');
    print '*******************************************************';
    return flags_per_spw;
}




print_flagreport:= function(flags_per_spw){
    s := '';
    for( fraction in flags_per_spw){
        s := spaste(s, ' ', as_integer(fraction*100.0 +0.5));
    }
    return s;
}



