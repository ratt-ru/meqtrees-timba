#!/bin/sh

# runtest.sh: script to assay a test program
#
#  Copyright (C) 2002
#  ASTRON (Netherlands Foundation for Research in Astronomy)
#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#  $Id$


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
    \rm -f $1.run
    \cp $srcdir/$1.run .
fi

#
# Run assay
#
$lfr_share_dir/assay $1
