import sys
import os
import time
import os.path
import re
import sets

import Purr
from Purr import dprint,dprintf

class DataProduct (object):
  def __init__ (self,filename,policy="copy",comment="",rename=None,orig_filename=None,timestamp=None):
    # filename of data product. Absolute pathname for unsaved data products,
    # or just a basename when product has been saved to a LogEntry directory
    self.filename = filename;
    # original pathname to data product (where it was copied/moved from)
    self.orig_filename = orig_filename or filename;
    # For unsaved DPs: handling policy: "copy","move","ignore". 
    self.policy = policy;
    # For unsaved DPs: if not None, DP will be renamed during copy/move.
    self.rename = rename or os.path.basename(filename);
    # Comment associated with DP
    self.comment = comment;
    # For saved DPs: timestamp of data product at time of copy
    self.timestamp = timestamp;
  
class LogEntry (object):
  """This represents a LogEntry object""";
  def __init__ (self,timestamp=None,title=None,comment=None,dps=[],load=None):
    self.timestamp,self.title,self.comment,self.dps = timestamp,title,comment,dps;
    self.pathname = None;
    if load:
      self.load(load);
    
  _entry_re = re.compile(".*/entry-(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)$");
  
  def isValidPathname (name):
    return os.path.isdir(name) and LogEntry._entry_re.match(name);
  isValidPathname = staticmethod(isValidPathname);
  
  def load (self,pathname):
    """Loads entry from directory entry""";
    match =self. _entry_re.match(pathname);
    if not match:
      return None;
    if not os.path.isdir(pathname):
      raise ValueError,"%s: not a directory"%pathname;
    if not os.access(pathname,os.R_OK|os.W_OK):
      raise ValueError,"%s: insufficient access privileges"%pathname;
    # parse index.html file
    parser = Purr.Parsers.LogEntryIndexParser();
    for line in file(os.path.join(pathname,'index.html')):
      parser.feed(line);
    # set things up
    self.timestamp,self.title,self.comment,self.dps = \
            parser.timestamp,parser.title,parser.comments,parser.dps;
    self.pathname = pathname;
      
  def save (self,dirname=None):
    """Saves entry in the given directory. Data products will be copied over if not
    residing in that directory.
    """;
    if dirname:
      self.pathname = pathname = os.path.join(dirname,
                        time.strftime("entry-%Y%m%d-%H%M%S",time.localtime(self.timestamp)));
    elif not self.pathname:
      raise ValueError,"Cannot save entry: pathname not specified";
    else:
      pathname = self.pathname;
    pathname = os.path.normpath(os.path.realpath(pathname));
    # now save content
    if not os.path.exists(pathname):
      os.mkdir(pathname);
    # get device of pathname -- need to know whether we move or copy
    devnum = os.stat(pathname).st_dev;
    # copy data products as needed
    dps = [];
    for dp in self.dps:
      # filename without a directory indicates already-saved data product, so ignore it
      if not os.path.dirname(dp.filename):
        dps.append(dp);
        continue;
      # ignored data product -- keep in list, but do nothing else
      if dp.policy == "ignore":
        dps.append(dp);
        continue;
      # file missing for some reason -- skip data product entirely
      if not os.path.exists(dp.filename):
        dprintf(2,"data product %s missing, ignoring\n");
        continue;
      # get normalized source and destination paths
      dprintf(2,"data product: %s, rename %s, policy %s\n",dp.filename,dp.rename,dp.policy);
      filename = os.path.normpath(os.path.realpath(dp.filename));
      destname = os.path.join(pathname,(dp.rename and os.path.basename(dp.rename)) or os.path.basename(filename));
      dprintf(2,"data product: %s -> %s\n",filename,destname);
      dp.filename = os.path.basename(destname);
      dp.orig_filename = filename;
      dp.rename = None;
      # does the destination product already exist? skip if same file, else remove
      if os.path.exists(destname):
        if os.path.samefile(destname,filename):
          dprintf(2,"same file, skipping\n");
          dp.timestamp = os.path.getmtime(destname);
          dps.append(dp);
          continue;
        if os.system("/bin/rm -fr %s"%destname):
          print "Error removing %s, which is in the way of %s"%(destname,filename);
          print "This data product is not saved.";
          continue;
      # now copy/move it over
      if dp.policy == "copy":
        dprintf(2,"copying\n");
        if os.system("/bin/cp -ua %s %s"%(filename,destname)):
          print "Error copying %s to %s"%(filename,destname);
          print "This data product is not saved.";
          continue;
      elif dp.policy.startswith('move'):
        # files or directories on same device may be moved directly
        if not os.path.isdir(filename) or os.stat(filename).st_dev == devnum:
          dprintf(2,"same filesystem, moving\n");
          if os.system("/bin/mv -fu %s %s"%(filename,destname)):
            print "Error moving %s to %s"%(filename,destname);
            print "This data product is not saved.";
            continue;
        # else copy, then remove
        else:
          dprintf(2,"different filesystem, copying & removing\n");
          if os.system("/bin/mv -fu %s %s"%(filename,destname)):
            print "Error moving %s to %s"%(filename,destname);
            print "This data product is not saved.";
            continue;
          os.system("/bin/rm -fr %s"%filename);
      # success, set timestamp and append
      dp.timestamp = os.path.getmtime(destname);
      dps.append(dp);
    # reset list of data products
    self.dps = dps;
    # now write out content
    dprint(3,"title",self.title,"comment",self.comment);
    outfile = file(os.path.join(pathname,"index.html"),"wt");
    Purr.Parsers.writeLogEntryIndex(outfile,self,full=True);
    
  def remove_directory (self):
    """Removes this entry's directory from disk""";
    if not self.pathname:
      return;
    if os.system("/bin/rm -fr %s"%self.pathname):
      print "Error removing %s";
    
  def timeLabel (self):
    return time.strftime("%x %X",time.localtime(self.timestamp));
   
      
