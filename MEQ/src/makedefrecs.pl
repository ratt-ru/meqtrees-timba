#!/usr/bin/perl

@ARGV>1 or die "Usage: $0 <defrec file> <list of headers>";

# set the verbose flag
$verbose = 1 if grep /^-v/,@ARGV;

my $mapname := '_meqdefrec_map';

my %fields;           # map: classname->[ list of field names ]
my %field_defaults;   # map: classname->{ map field->default ]
my %field_desc;       # map: classname->{ map field->[list of description lines] }
my %parent;           # map: classname->parent class (if any)
my %class_desc;       # map: classname->[ list of class description lines]
my %srcfile;					# map: classname->source file

# loop over all headers
for( @ARGV )
{
  # ignore verbose flag
  next if /^-v/;
  # set output file, if not set
  unless( $output_file )
  {
    $output_file = $_;
    next;
  }
  $infile = $_;
  # otherwise, it's a header
  open INFILE,"<$infile" or die "Can't open input file $infile: $!";
  $verbose and printf STDERR "Processing header file $infile\n";
  # nodeclass becomes non-empty inside a defrec declaration
  my ($nodeclass,$field);
  undef $nodeclass;
  undef $field;
  while( <INFILE> )
  {
    my $line = $_;
    chop $line;
    next unless $line =~ s/^\/\/ ? ?//; # strip leading //, skip if none
                                  # (also strips up to two leading spaces)
    # defrec begin opens a node class declaration
    if( $line =~ /^\s*defrec\s+begin\s+(\w+)(:\w+)?\b/ )
    {
      not $nodeclass or die "'defrec begin' inside of a defrec block";
      $nodeclass = $1;
      $2 and $parent{$nodeclass} = substr($2,1);
      $srcfile{$nodeclass} = $infile;
      $class_desc{$nodeclass} = [];
      $fields{$nodeclass} = [];
      $field_defaults{$nodeclass} = {};
      $field_desc{$nodeclass} = {};
      $verbose and printf STDERR "  begin class $nodeclass " .
        ( $parent{$nodeclass} ? "parent $parent{$nodeclass}" : "" ) . "\n";
      undef $field;
    }
    # defrec end ends a declaration
    elsif( $line =~ /^\s*defrec\s+end/ )
    {
      $nodeclass or die "'defrec end' outside of a defrec block";
      undef $nodeclass;
    }
    # field: name default_value declares a field
    elsif( $line =~ s/^\s*field:\s+// )
    {
      next unless $nodeclass; # ignore outside of begin/end block
      ($field,$value) = split /\s+/,$line,2;
      push @{$fields{$nodeclass}},$field;
      $verbose and printf STDERR "    field $field = $value\n";
      $field_defaults{$nodeclass}->{$field} = $value;
      $field_desc{$nodeclass}->{$field} = [];
    }
    # any other comment added to description of previous field or class
    else  # else free-form comment to be added to last field
    {
      next unless $nodeclass; # ignore outside of begin/end block
      $line =~ s/(['"])/\\\1/g;
      if( defined $field ) { # add to description of previous field
        push @{$field_desc{$nodeclass}->{$field}},$line;
        $verbose and printf STDERR "    # $line\n";
      } else { # add to class description
        push @{$class_desc{$nodeclass}},$line;
        $verbose and printf STDERR "  # $line\n";
      }
    }
  }
}
#
# now partially sort the classes from parent to child
@classlist = sort { return $a eq $parent{$b} ? -1 : 0 } keys %fields;

my $today=`date`;
open OUTFILE,">$output_file" or die "Can't open output file $output_file: $!";
print OUTFILE <<______END_OF_QUOTE;
# This file is generated automatically -- do not edit
# Original file name: $output_file
# Generated on $today
# Defines the default init records ("defrecs") for all the nodes in a 
# given package. This file is meant to be included inside a function that 
# fills out the defrecs.
# 
______END_OF_QUOTE

foreach $class ( @classlist )
{
  # print out class name and initial record (perhaps derived from parent)
  $src = "# generated from $srcfile{$class}\n#";
  print OUTFILE "#\n# ---------- class $class";
  if( $parent{$class} ) {
    print OUTFILE " (derived from $parent{$class})\n$src\nr := $mapname.$parent{$class};\n";
  } else {
    print OUTFILE "\n$src\nr := $mapname.MeqNode;\n";
  }
  # make class description
  $hdr1 = "r::description := '";
  $hdr2 = " \\\n" . (" " x length($hdr1));
  print OUTFILE $hdr1,join($hdr2,@{$class_desc{$class}}),"';\n";
  # now make the fields
  foreach $field (@{$fields{$class}}) {
    # make field definition
    print OUTFILE "r.$field := ",$field_defaults{$class}->{$field},";\n";
    # make field description
    if( @{$field_desc{$class}->{$field}} ) {
      $hdr1 = "r.${field}::description := '";
      $hdr2 = " \\\n" . (" " x length($hdr1));
      print OUTFILE $hdr1,join($hdr2,@{$field_desc{$class}->{$field}}),"';\n";
    }
  }
  # store in defrec
  print OUTFILE "$mapname.$class := r;\n";
}
close OUTFILE;
