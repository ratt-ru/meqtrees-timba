#!/bin/sh
#
#  limitexec.sh: script to limit the runtime of an executable
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

#
# A poor man's implementation of LimitExec.
#

if test $# -lt 2; then
  echo "Usage: limitexec.sh <max-runtime(sec)> <executable> [<arguments>]" >&2
  exit 1
fi

MAXTIME=$1
PROGRAM=$2
shift 2

# Start the program specified by $PROGRAM in the background.
$PROGRAM $* &

# Check every second if the program is still running. Kill the program
# when the maximum execution time, specified by $MAXTIME, has elapsed.
# Note: pid of last started background program is $!.
sec=0
while ps | awk '{print $MAXTIME}' | grep $! >/dev/null; do
  if test $sec -ge $MAXTIME; then
    echo "limitexec.sh: Process $! has exceeded time limit and will be killed." >&2
    kill -9 $!
    exit 255
  fi
  sec=`expr $sec + 1`
  sleep 1
done
