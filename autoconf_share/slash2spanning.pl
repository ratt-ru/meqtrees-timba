#!/usr/bin/perl
#
#  slash2spanning.pl: Convert multiple C++ "slash-slash" style comment lines
#                     into one spanning C-style comment (/* ... */), ignoring
#                     lines that start with "slash-slash-hash style comments.
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

$NON_COMMENT_BLOCK = 0;
$COMMENT_BLOCK     = 1;

# If the caller supplied precisely one command line argument, then this script
# can proceed.
$arguments = @ARGV;
if ($arguments == 1)
{
  # The argument represents the name of the file to process.
  $filename = $ARGV[0];

  # Get current directory.
  $cwd = `pwd`;
  chop($cwd);
  $cwd =~ s|/$||;
  # Append file name to it (which may contain a path as well).
  $filnm = $cwd . "/" . $filename;
  # Get the name of the package.
  $pkgnm = $filnm;
  $pkgnm =~ s%/include/.*%%;
  $pkgnm =~ s%/src/.*%%;
  $parentnm = $pkgnm;
  $pkgnm =~ s%.*/%%;
  $parentnm =~ s%/[^/]+$%%;
  $parentnm =~ s%.*/%%;
  # Get the name of the file from LOFAR on.
  $filnm =~ s%.*/LOFAR/%LOFAR/%;

  # Open the file.
  $status = open(FILEHANDLE, $filename);

  # If the file could be opened then read the contents.
  if ($status)
  {
    # Read the contents of the file.
    @text = <FILEHANDLE>;

    # Close the file.
    close(FILEHANDLE);

    # Process the contents of the file.
    change_comment_style(@text);
  }

  # Otherwise report an error condition.
  else
  {
    print "ERROR: file \"$filename\" could not be opened.\n";
  }
}

# Otherwise, display the proper invocation for this script.
else
{
  print "usage: $0 filename\n";
}

sub change_comment_style
{
  $keephash = 1;
  $state = $NON_COMMENT_BLOCK;
  $newstate = $NON_COMMENT_BLOCK;
  @spanning_comment = ();
  $indent = "";
  $comment = "";

  foreach $line (@_)
  {
    # Replace the various placeholders.
    $line =~ s/%pkgname%/$pkgnm/;
    $line =~ s/%parentpkgname%/$parentnm/;
    $line =~ s/%filename%/$filnm/;
    $newstate = $NON_COMMENT_BLOCK;
    # slash-slash-hash is blanked if not at beginning of file..
    if ($keephash == 0  &&  $line =~ /^\s*\/\/\#/)
    {
      $line = "\n";
    }
    $comment = $line;
    # If this line contains only a slash-slash comment, then
    # the comment block might need to be converted.
    if ($line =~ /(^\s*)(\/\/)(.*)/)
    {
      # Keep track of how far the comment block is indented.
      $indent = $1;
      $comment = $3;
      # slash-slash-slash/hash are kept as such (is doxygen already).
      if ($comment !~ /^[\/#]/)
      {
        $keephash = 0;
	$newstate = $COMMENT_BLOCK;
	# Replace <srcblock> by \code
	$comment =~ s/<srcblock>/\\code/g;
	$comment =~ s/<\/srcblock>/\\endcode/g;
	# Replace <summary> by \brief
	$comment =~ s/<summary>/\\brief/g;
	$comment =~ s/<\/summary>//g;
	# Handle group comments and keep // in doxygen groups.
	$comment =~ s/<group>/@\{/g;
	$comment =~ s/<\/group>/@\}/g;
	if ($comment =~ /^\s*@[\{\}]\s*$/)
	{
	  $comment =~ s/\s*//g;
	  $line = "$indent//$comment\n";
	  $newstate = $NON_COMMENT_BLOCK;
	}
      }
      # A blank line does not change anything.
      elsif ($line =~ /^\s*$/)
      {
	$newstate = $state;
      }
    } else {
      $keephash = 0;
    }

    # Act depending on new and old state.
    if ($newstate == $COMMENT_BLOCK) {
      if ($state == $COMMENT_BLOCK) {
	# Add comment to block.
	push @spanning_comment, "\n$indent   $comment";
      } else {
	# Begin the spanning comment block with given indentation.
	push @spanning_comment, "$indent\/**$comment";
      }
    } else {
      if ($state == $COMMENT_BLOCK) {
	# End comment block and write the block.
	push @spanning_comment, " */\n";
	print @spanning_comment;
	@spanning_comment = ();
      }
      # Write the line.
      print $line;
    }
    $state = $newstate;
  }

  # Output remaining comments if there.
  if ($state == $COMMENT_BLOCK)
  {
    push @spanning_comment, " */\n";
    print @spanning_comment;
  }
}

