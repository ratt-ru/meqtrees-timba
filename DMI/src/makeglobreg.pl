#!/usr/bin/perl

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

@ARGV==2 or die "Usage: $0 <global list file> <Output registry file>.cc";

my ($infile,$outfile) = @ARGV;

open INFILE,"<$infile" or die "Can't open input file $infile: $!";
open OUTFILE,">$outfile" or die "Can't open output file $outfile: $!";

print OUTFILE <<______END_OF_QUOTE;
    // This file is generated automatically -- do not edit
    #include "AtomicID.h"
    using namespace DMI;

    int aidRegistry_Global ()
    {
      static int res = 

______END_OF_QUOTE

$line = 0;
while( <INFILE> )
{
  $line++;
  next if /^\s*$/ or /^\s*;/;
  if( /\s*(\w+)\s+(\d+)\s*(; from (.*))?$/ ) {
    my ($id,$num,$dum,$from) = (lc $1,$2,$3,$4);
    print OUTFILE "        AtomicID::registerId(-$num,\"$id\")+\n";
    $count++;
  } else {
    print STDERR "$infile:$line: warning: unable to parse this line, skipping\n";
  }
}

close INFILE;
print OUTFILE <<______END_OF_QUOTE;
    0;
    return res;
  }
  
  int __dum_call_registries_for_Global = aidRegistry_Global();

______END_OF_QUOTE
close OUTFILE;
print STDERR "=== wrote $count registry entries to $outfile\n";

