#!/bin/bash
REQUIRES="../src/meqserver ../pkginc/*/*.g"

for file in $REQUIRES; do
  localname=${file##*/}
  rm -f $localname
  ln -s $file .
done

echo "Running solver_test.g"
echo >solver_test.log
tail +0f solver_test.log &
tailpid=$!
glish -l ${srcdir}/solver_test.g -runtest &>solver_test.log
retval=$?
echo "Glish exited with status $retval"
kill $tailpid 
exit $retval
