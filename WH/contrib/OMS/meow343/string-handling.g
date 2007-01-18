include 'quanta.g';

empty_string := function(input)
{
    return length(split(input)) == 0;
}

strip := function(input)
{
    if (empty_string(input)){
        return '';
    }
    return input ~ s/\s*(.*\S)\s*$/$1/g;
}

spaste_taql_array := function(arr)
{
    return strip(spaste(arr)) ~ s/ /,/g;
}


query_antennae:= function (antids)
{
    if(is_boolean(antids) || len(antids)==0){
        return '';
    }
    arr:= spaste_taql_array(antids-1);
    return paste('((ANTENNA1 in', arr, ')|| (ANTENNA2 in',arr,'))');
}

query_spwids := function(spwids)
{
    if(is_boolean(spwids) || len(spwids)==0){
        return '';
    }
    arr:= spaste_taql_array(spwids-1);
    return paste('(DATA_DESC_ID in', arr, ')');
}

query_timerng := function(timerng)
{
    global system;
    pp := system.print.precision;
    system.print.precision:=12;
    
    if(is_boolean(timerng) || len(timerng) < 2){
        return '';
    }
    tmMin := dq.convert(timerng[1]).value;
    tmMax := dq.convert(timerng[2]).value;

     
    query := paste('((TIME_CENTROID >=',tmMin, ') && (TIME_CENTROID <=',tmMax, '))');
    system.print.precision := pp;
    return query;
}

append_if_nonempty := function(part1, part2, sep=' && ')
{
    if(part1 == ''){
        return part2;
    }else if(part2 == ''){
        return part1;
    }else{
        return spaste(part1, sep, part2);
    }
}
