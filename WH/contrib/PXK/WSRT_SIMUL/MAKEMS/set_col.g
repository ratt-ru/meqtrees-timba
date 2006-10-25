#! /bin/bash -f

pragma include once

func set_col(ms='', whatcol='', val=1) {
    # Sets column 'whatcol' to val 
    include 'table.g'
    t    := table(ms, readonly=F);
    print shape(t); 
    a    := t.getcol(whatcol)
    a[:] := val
    t.putcol(whatcol, a)
    t.done(); 
} 


# parse command line
for( a in argv )
{
  print 'arg: ',a;
  if( a =~ s/ms=// )
    msname := a;
  else if( a =~ s/col=// )
    col := a;
  else if( a =~ s/val=// )
    val := a;
}
print "MS name is ",msname; 

set_col(msname, col, val)