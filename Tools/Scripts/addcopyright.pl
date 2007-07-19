#!/usr/bin/perl
#This script will add a copyright notice to python/shell/perl script files
# $Id$ 

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

if (scalar(@ARGV) ==0) {
   &usage;
   exit(1);
}


#### patterns
$skip_lines='^\s$|^#.*$';
$old_copyright='^# GNU General Public License .*$';
$tmpfile_name="./.tmpfile";

for ($argnum=0; $argnum<=$#ARGV; $argnum++) {
#printf "Adding GPL to @ARGV[$argnum]\n";
# open files
$filename = @ARGV[$argnum];
open(IN,"< @ARGV[$argnum]") || die "can't open file @ARGV[$argnum] for reading\n";
open(OUTFILE,"> $tmpfile_name") || die "cant' open file $tmpfile_name for writing\n";

if( $filename =~ /\.(C|cc|h)$/ ) {
  print "$filename: is a C++ file, using '//' comment style\n";
  $cmt = '//';
  $skip_lines='^\s$|^//.*$';
  $old_copyright='GNU General Public License';
} else {
  print "$filename: non-C++, using '#' comment style\n";
  $cmt = '#';
  $skip_lines='^\s$|^#.*$';
  $old_copyright='GNU General Public License';
}
  
$written_header=0;
$has_copyright = 0;
$meqtree_copyright = 0;
$astron_copyright = 0;
$add_id_line = 1;
# read file
while (defined($sline = <IN>)) {
  if (!$written_header ) {
    if ($sline =~ /($skip_lines)/ ) {
      # is this an $Id$ comment?
      if( $sline =~ /\$Id.*\$/ ) {
        $add_id_line = 0;
        print "$filename: \$Id\$ comment found\n";
      }
      # adjust copyright dates, if any
      if( $sline =~ /Copyright \(C\) 2002-2007/ ) {
        print "$filename: copyright 2002-2007 found\n";
      }
      elsif ( $sline =~ s/Copyright \(C\) 200[0-9-]+/Copyright (C) 2002-2007/ ) {
        $has_copyright = 1;
        print "$filename: adjusting copyright dates\n";
      }
      # otherwise flag the fact that we have a copyright notice
      if( $sline =~ /Copyright \(c\)/ ) {
        $has_copyright = 1;
        print "$filename: other copyright notice found\n";
      }
      # do we have a meqtree copyright?
      if( $sline =~ /MeqTree Foundation/ ) {
        $meqtree_copyright = 1;
        print "$filename: MeqTree copyright notice found\n";
      }
      # have we hit an astron copyright address?
      if( $sline =~ /^([^a-zA-Z]+).*Dwingeloo/ ) {
        if( !$meqtree_copyright ) {
          # no meqtree copyright, insert
          print "$filename: adding MeqTree copyright to ASTRON notice\n";
          print OUTFILE "$1and The MeqTree Foundation\n";
        }
      }
      # print to output
      print OUTFILE $sline;
      if ( $sline =~ m/($old_copyright)/ ) {
        # copyright already exists
        print "$filename: GPL notice found\n";
        $written_header=1;
      }
    } else {
        # write the header here, if no other copyright notice appears
        if( $has_copyright ) {
          print "$filename: other copyright found, skipping header\n";
        } else {
          print "$filename: inserting full header\n";
          &print_copyright($add_id_line);
        }
        $written_header=1;
  
        print OUTFILE $sline;
      } 
  } else {
    # we have already written header, copy input to output
     print OUTFILE $sline;
  }

}

# now we are at the end of file, if we still have not
# added the header, do so now

if (!$written_header ) {
     &print_copyright($add_id_line);
}

close (IN) || die "can't close input file $!";
close (OUTFILE) || die "can't close output file $!";

# copy new file to original location
$cmd="/bin/cp $tmpfile_name @ARGV[$argnum]";
system($cmd)==0  or die "can't update file @ARGV[$argnum] for reading\n";

}

# remove any temporary files created
unlink($tmpfile_name) or die "can't delete $tmpfile_name: $!\n";

##########################################################
#### help
sub usage {
  printf "Usage: $0 [input files]\n";
  printf "[input files] are the files you need to add copyright to\n";
}


##########################################################
#### print copyright
sub print_copyright {
  my ($add_id) = @_;
  if( $add_id )
  {
    print OUTFILE "$cmt\n";
    print OUTFILE "$cmt% \$Id\$ \n";
    print OUTFILE "$cmt\n";
  }

  print OUTFILE "$cmt
$cmt Copyright (C) 2002-2007
$cmt The MeqTree Foundation & 
$cmt ASTRON (Netherlands Foundation for Research in Astronomy)
$cmt P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
$cmt
$cmt This program is free software; you can redistribute it and/or modify
$cmt it under the terms of the GNU General Public License as published by
$cmt the Free Software Foundation; either version 2 of the License, or
$cmt (at your option) any later version.
$cmt
$cmt This program is distributed in the hope that it will be useful,
$cmt but WITHOUT ANY WARRANTY; without even the implied warranty of
$cmt MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
$cmt GNU General Public License for more details.
$cmt
$cmt You should have received a copy of the GNU General Public License
$cmt along with this program; if not, see <http://www.gnu.org/licenses/>,
$cmt or write to the Free Software Foundation, Inc., 
$cmt 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
$cmt\n";

  print OUTFILE "\n";
}
