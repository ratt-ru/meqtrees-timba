map1 := function(fn, list)
{
    if(len(list) > 0){
        for(i in 1:len(list)){
            result[i] := fn(list[i]);
        }
        return result;
    }
    return F;
}

map2 := function(fn, list1, list2)
{
    if(len(list1) > 0){
        for(i in 1:len(list1)){
            result[i] := fn(list1[i], list2[i]);
        }
        return result;
    }
    return F;
}


map3 := function(fn, list1, list2, list3)
{
    if(len(list1) > 0){
        for(i in 1:len(list1)){
            result[i] := fn(list1[i], list2[i], list3[i]);
        }
        return result;
    }
    return F;
}


map4 := function(fn, list1, list2, list3, list4)
{
    if(len(list1) > 0){
        for(i in 1:len(list1)){
            result[i] := fn(list1[i], list2[i], list3[i], list4[i]);
        }
        return result;
    }
    return F;
}


map := function(fn, ...)
{
    map_functions    := [=];
    map_functions[1] := map1;
    map_functions[2] := map2;
    map_functions[3] := map3;
    map_functions[4] := map4;
    
    return map_functions[num_args(...)](fn, ...);
}


reduce := function(fn, list, initial_value=F, use_initial_value=F)
{
    if(len(list) < 2){
        return F;
    }
    start   := 2;
    current := list[1];
    if(use_initial_value){
        start := 1;
        current := initial_value;
    }
    for(i in start:len(list)){
        current := fn(current, list[i]);
    }
    return current;
}



print_fn := function(...)
{
    print paste(...);
    return T;
}



# fn is a function of (table_object, start_row, nrows)
# The function should return T on success, F on failure;
# This function can be used to iterate over MS table objects in case of 
# limited memory
map_ms := function(fn, table_object,...)
{
    if(is_fail(table_object)){
        print table_object;
        return F;
    }
    result_list := [=]

    chunksize    := 200.0e+6; # Bytes
    elem_per_row := prod(shape(table_object.getcell('DATA',2)));
    nrows        := floor(chunksize/elem_per_row/(4*16));

    totalrows := table_object.nrows();
    start     := 1;
 
    ix := 1;
    
    while(start <= totalrows) {
        print start, '/', totalrows;
        if(start+nrows-1 > totalrows){
            nrows := totalrows - start + 1;
        }
        result_list[ix]:= fn(table_object, start, nrows, ...);
        start +:= nrows;
        ix+:=1;
    }
    return result_list;
}
