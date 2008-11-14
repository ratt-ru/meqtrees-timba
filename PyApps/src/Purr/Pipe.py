"""Purr.Pipe is a very lightweight module for writing to Purr pipes.
It is meant to be used within TDL scripts and such."""

import os.path
import traceback

_pipefile = ".purr.pipe";

class Pipe (object):
  """The Pipe class represents a Purr pipe.""";
  def __init__ (self,dirname):
    """opens a Purr pipe to the specified directory""";
    self.dirname = dirname;
    global _pipefile;
    file = os.path.join(dirname,_pipefile);
    self.pipefile = os.path.abspath(os.path.normpath(os.path.realpath(file)));
    self.pipefile_read = os.path.abspath(os.path.normpath(os.path.realpath(file)))+".read";
    self.mtime = 0;
    
  # writer section
  
  def _write (self,what):
    """writes something to the Purr pipe""";
    try:
      file(self.pipefile,"a").write(what);
    except:
      print "Error writing to %s:"%self.pipefile;
      traceback.print_exc();
  
  def title (self,title,show=False):
    """writes a title tag to the Purr pipe""";
    self._write("title:%d:%s\n"%(int(show),title));
    return self;
  
  def comment (self,comment,show=False,endline=True,newpar=False):
    """writes a comment tag to the Purr pipe""";
    if not endline:
      comment += "<NOBR>";
    if newpar:
      comment += "<BR>";
    self._write("comment:%d:%s\n"%(int(show),comment));
    return self;
    
  def __lshift__ (self,comment):
    """<< is equivalent to writing a comment""";
    return self.comment(comment);
    
  def pounce (self,file,show=False):
    """writes a pounce command to the Purr pipe""";
    file = os.path.abspath(os.path.normpath(os.path.realpath(file)));
    self._write("pounce:%d:%s\n"%(int(show),file));
    return self;
    
  # reader section
  def read (self):
    """Checks if anything has arrived in the pipe file, returns list of 
    (command,show,content) tuples.
    Special tags added in comment() above are replaced.
    """;
    # read file is set to None on error, so that we stop reading
    if self.pipefile_read is None:
      return [];
    # no pipe -- read nothing
    if not os.path.exists(self.pipefile):
      return [];
    # move pipe file out of the way before we start reading from it
    try:
      os.rename(self.pipefile,self.pipefile_read);
    except:
      print "Error renaming %s to %s:"%self.pipefile,self.pipefile_read;
      traceback.print_exc();
      self.pipefile_read = None;
      return [];
    # now read everything
    try:
      lines = file(self.pipefile_read).readlines();
    except:
      print "Error reading %s:"%self.pipefile_read;
      traceback.print_exc();
      self.pipefile_read = None;
      return [];
    # parse lines 
    cmds = [];
    for line in lines:
      tokens = line.rstrip().split(":",2);
      if len(tokens) < 3:
        continue;
      command,show,content = tokens;
      # convert 'show' to bool
      try:
        show = bool(int(show));
      except:
        show = False;
      # if 'comment' command, parse content string
      if command == "comment":
        # <BR> inserts new paragraph (double-newline)
        content = content.replace("<BR>","\n\n");
        # <NOBR> blocks newline at end, which is otherwise implictly added...
        if content.endswith("<NOBR>"):
          content = content[:-6];
        # ...here
        elif not content.endswith("\n"):
          content += "\n";
      # add to list of contents
      # print "read %s:%d:%s:"%(command,show,content);
      cmds.append((command,show,content));
    return cmds;
  
def open (dirname):
  return Pipe(dirname);

