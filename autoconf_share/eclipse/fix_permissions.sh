#!/bin/sh

#
# Do chmod +x on all Bourne shell files in the current directory
# and all recursive sub-directories.
#

#
# Get list of Bource shell files
#
files=`/usr/bin/find . -exec /usr/bin/file -L {} \; | grep Bourne | cut -d: -f1`

#
# Run chmod +x on all files 
#
for f in $files; do
	echo running "chmod +x $f";
	chmod +x $f;
done
