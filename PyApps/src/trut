#!/bin/bash

args=""
files=""
help=""

while [ "$1" != "" ]; do
  if [ "$1" == "-h" -o "$1" == "--help" ]; then
    help=1
    break;
  elif [ "${1#-*}" == "$1" ]; then
    files="$files $1"
  else
    args="$args $1";
  fi
  shift
done

if [ -z "$files" -a -z "$help" ]; then
  files=`find . -type f -name TRUT`
  if [ -z "$files" ]; then
    echo -n "No TRUT files were specified, and none were found under "
    pwd
    exit 1;
  fi
fi

if [ "$help" != "" ]; then
  cat <<-'endusage'
  
	  TRUT: Timba Reduction & Unit Testing
          
	  Usage: trut [-jN] [-vN] [-lN] [-pN] [-dContext=level] [trutfiles...]
          
	    -jN: run up to N tests in parallel (set to # of CPUs).
	    -vN: set console verbosity level (default is 21 -- try increments of 10).
	    -lN: set trut.log verbosity level (default is 41).
	    -pN: set persistence level (default is 0). Use >0 to keep running when tests fail.
	    -dContext=level: enable debug messages from given Python context
            
	  If no trutfiles are specified, all TRUT files in the current directory tree will be found & used.
          
	endusage
  exit 1;
fi

exec trut.py $args $files

