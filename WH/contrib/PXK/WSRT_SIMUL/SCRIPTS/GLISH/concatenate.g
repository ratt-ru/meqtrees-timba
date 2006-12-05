# glish/aips++ script to concatenate ms files
# History
# - 2006.11.03: creation

pragma include once

# Default inputs
NAME1:=F
NAME2:=F

# parse command line
for( a in argv )
{
  print 'arg: ',a;
  if     ( a =~ s/ms1=// )
    NAME1:=a;
  else if( a =~ s/ms2=// )
    NAME2:=a;
}

# check input
if (NAME1==F || NAME2==F){
  print "Usage: glish concatenate.g ms1=FILE1.MS ms2=FILE2.MS"
  exit
}


include 'ms.g'

print ""
print "________________________________________________________"
print "MS1 name is", NAME1;
print "MS2 name is", NAME2, " (will be appended to MS1)"
print "________________________________________________________"
print ""

ms_001 := ms(NAME1, readonly=F)
ms_001.concatenate(NAME2)
# MS   := msplot(NAME1)
exit

