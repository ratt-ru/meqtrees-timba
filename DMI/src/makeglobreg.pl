#!/usr/bin/perl

@ARGV==2 or die "Usage: $0 <global list file> <Output registry file>.cc";

my ($infile,$outfile) = @ARGV;

open INFILE,"<$infile" or die "Can't open input file $infile: $!";
open OUTFILE,">$outfile" or die "Can't open output file $outfile: $!";

print OUTFILE <<______END_OF_QUOTE;
    // This file is generated automatically -- do not edit
    #include "AtomicID.h"

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

