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
    $state = $NON_COMMENT_BLOCK;
    @spanning_comment = ();
	$indent = "";
    $comment = "";

    foreach $line (@_)
    {
        if ($state == $NON_COMMENT_BLOCK)
        {
            # If this line contains only a slash-slash comment, then
            # we're at the beginning of a comment block.
            if ($line =~ /(^\s*)(\/\/)(.*)/)
            {
                $state  = $COMMENT_BLOCK;

                # Keep track of how far the comment block is indented.
                $indent = $1;
                $comment = $3;

                # Begin the spanning comment block.
                push @spanning_comment, "$1\/**\n";

                # Add the comment that follows, but ONLY if the comment
                # does not start with a hash character.
                if ($comment !~ /^\#/)
                {
                    push @spanning_comment, "$indent $comment\n";
                }
            }

            # Otherwise, we're not within a comment block.
            else
            {
                print $line;
            }
        }
        elsif ($state == $COMMENT_BLOCK)
        {
            # If this line contains only a slash-slash comment, then
            # we're still within a comment block.
            if ($line =~ /(^\s*)(\/\/)(.*)/)
            {
                $indent = $1;
                $comment = $3;

                if ($comment !~ /^\#/)
                {
                    push @spanning_comment, "$indent $comment\n";
                }
            }

            # Otherwise, the comment block has ended and the spanning
            # comment needs to be emitted.
            else
            {
                $state = $NON_COMMENT_BLOCK;
                push @spanning_comment, "$indent */\n";
                print @spanning_comment;
                @spanning_comment = ();
                print $line;
            }
        }
        else
        {
            $state = $NON_COMMENT_BLOCK;
        }
    }
}

