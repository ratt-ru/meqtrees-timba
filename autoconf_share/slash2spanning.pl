#!/usr/bin/perl
#******************************************************************************
# Program:    slash2spanning.perl
# Programmer: John Moren
# Date:       17-Sep-2001
#
# Brief description:
#
# This program replaces lines of text that consist of "slash-slash" style 
# comments (// a comment) with spanning style comments (/* ... */). The output
# of this program is directed to the standard output device. The contents of 
# the comments are not altered.
#
# Calling convention:
#
# Argument   Description
# ---------------------------------------------------------------------------
#     0      The name of the file to process
#
#******************************************************************************

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

                # Add the comment that follows. If the comment begins
                # with a slash character, then add a space character
                # between the "*" character and the comment (since "*/"
                # terminates a spanning comment block).
                if ($comment =~ /^\//)
                {
                    push @spanning_comment, "$indent * $comment\n";
                }
                else
                {
                    push @spanning_comment, "$indent *$comment\n";
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

                if ($comment =~ /^\//)
                {
                    push @spanning_comment, "$indent * $comment\n";
                }
                else
                {
                    push @spanning_comment, "$indent *$comment\n";
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

