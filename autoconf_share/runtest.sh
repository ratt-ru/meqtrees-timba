#!/bin/sh

if test $# -ne 1; then
  echo usage: runtest.sh testname
  exit 0
fi

#
# Copy expected files to current directory
#
if test -f $srcdir/$1.in; then
    \cp $srcdir/$1.in  .
fi
if test -f $srcdir/$1.out; then
    \cp $srcdir/$1.out .
fi
if test -f $srcdir/$1.run; then
    \cp $srcdir/$1.run .
fi

#
# Run assay
#
lofar_dir=`dirname $0`
$lofar_dir/assay $1
