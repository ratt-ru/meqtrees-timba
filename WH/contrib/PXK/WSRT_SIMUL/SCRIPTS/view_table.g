#! /bin/bash -f       # just for colors
# glish/aips++ script to view table
#
# History: 
#  - 2006.12.04: creation

# system.output.log := "./lala.txt"

pragma include once

## FUNCTIONS ####################################
function view_table(MS){
    include 'table.g'

    # Get the data
    t       := table(MS)
		t.browse()
}


## MAIN PROGRAM #################################
if (len(argv)<1){
    print "";
    print "glish script.g msname=file"
    print ""
    exit
} else {

    # default arguments
    msname    := ""
    npix      := 512;

    # parse command line
    for( a in argv ){
    print 'arg: ',a;
    if     ( a =~ s/ms=// )       msname   := a;
    else if( a =~ s/npix=// )	    npix     := as_integer(a);
    }
		
		view_table(msname)
}
