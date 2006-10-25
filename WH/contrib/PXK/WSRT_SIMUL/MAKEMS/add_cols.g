#!/usr/bin/env python

pragma include once

func set_col(ms='', whatcol='', num=1) {
    # Sets column 'whatcol' to num 
    include 'table.g'
    t    := table(ms, readonly=F);
    print shape(t); 
    a    := t.getcol(whatcol)
    a[:] := num
    t.putcol(whatcol, a)
    t.done(); 
} 


func add_col(ms='', whatcol='', num=1.0) {
    # Sets column 'whatcol' to num 
    include 'table.g'
    t    := table(ms, readonly=F);

    col  := tablecreatearraycoldesc(whatcol, as_complex(0), 2, [4,32])
    t.addcols(tablecreatedesc(col))
    t.addcols(col)
    t.done(); 
} 

# parse command line
for( a in argv ) {
  print 'arg: ',a;
  if( a =~ s/ms=// )
    msname := a;
}
print "MS name is ",msname; 

#add_col (msname, MODEL_DATA,     1.0)
#add_col (msname, CORRECTED_DATA, 1.0)
#add_col (msname, IMAGING_WEIGHT, 1.0)
#set_col(msname, col, val)


