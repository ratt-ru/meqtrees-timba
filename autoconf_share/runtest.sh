#!/bin/sh

if test $# -ne 1; then
  echo usage: runtest.sh testname
  exit 0
fi

# Get directory of this script.
lfr_share_dir=`dirname $0`
lfr_share_dir=`cd $lfr_share_dir && pwd`

# Set source directory if not defined.
if [ "$srcdir" = "" ]; then
  curwd=`pwd`
  basenm=`basename $curwd`
  srcdir=$lfr_share_dir/../`cd .. && $lfr_share_dir/findpkg`/$basenm
fi

#
# Copy expected files to current directory
#
if test -f "$srcdir/$1.in"; then
    \cp $srcdir/$1.in  .
fi
if test -f "$srcdir/$1.out"; then
    \cp $srcdir/$1.out .
fi
if test -f "$srcdir/$1.run"; then
    \cp $srcdir/$1.run .
fi

#
# Run assay
#
$lfr_share_dir/assay $1
