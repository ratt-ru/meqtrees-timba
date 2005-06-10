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
# Note: $! expands to the process ID of last started background program.
sec=0
while kill -0 $! 2>/dev/null; do
  if test $sec -ge $MAXTIME; then
    echo "limitexec.sh: $PROGRAM (pid=$!) has exceeded time limit" \
         "($MAXTIME s) and will be killed" >&2
    kill -9 $! 2>/dev/null
    exit 255
  fi
  sec=`expr $sec + 1`
  sleep 1
done

# Once we reach here, $PROGRAM has already terminated. 
# To fetch its return status, however, we must call wait.
# Note: this trick does not work in some old Bourne shells where
# wait returns 0 when waiting for an already terminated process.
wait $! 2>/dev/null
