_tdl_no_reimport = True;

# TODO:
# - move Purr to PyApps, integrate into browser
#   - will need to provide TDLGUI services to TDL scripts
# - think of including verbatim code snippets in HTML
# - tools can write to ".purr.newentry" to automatically pop up and populate the NewEntry dialog

import sys
import os
import os.path
import re
import time
import traceback
import fnmatch
import sets
import signal
from qt import *

import Purr
from Purr import Config,dprint,dprintf;
import Purr.Parsers

def parse_pattern_list (liststr):
  """Parses a list of filename patterns of the form "Description=ptt,patt,...;Description=patt,...
  Returns list of (description,[patterns]) tuples."""
  _re_patt = re.compile("^(.*)=(.*)");
  patterns = [];
  for ss in liststr.split(';'):
    match = _re_patt.match(ss);
    if match:
      desc = match.group(1);
      patt = match.group(2).split(',');
      patterns.append((desc,patt));
  return patterns;
    
def make_pattern_list (patterns):
  """Makes a string of filename patterns from a list of (description,[patterns]) tuples."""
  pattstrs = [];
  for desc,patts in patterns:
    # ";," not allowed in descriptions or patterns
    patts = [ p.replace(";","").replace(",","") for p in patts ];
    desc = desc.replace(";","").replace(",","");
    pattstrs.append("%s=%s"%(desc,','.join(patts)));
  return ";".join(pattstrs);
  

class Purrer (QObject):
  def __init__ (self,parent,dirname,hide_on_close=False):
    QObject.__init__(self);
    self._mainwin = Purr.MainWindow((isinstance(parent,QWidget) and parent) or None,
                        self,hide_on_close=hide_on_close);
    self._default_dp_props = {};
    self._dir_timestamps  = {};
    self._file_timestamps = {};
    self._new_dps = sets.Set();
    # load directory content
    self.loadDirectory(dirname);
    self._timer = None;
    # load and parse configuration
    watch = Config.get("watch-patterns","TDL configuration=.tdl.conf;Image=*fits");
    self._watch = parse_pattern_list(watch);
    self._watch_patterns = sets.Set();
    for desc,patts in self._watch:
      self._watch_patterns.update(patts);
    dprint(1,"watching patterns",self._watch_patterns);
    ignore = Config.get("ignore-patterns","Internal Purr files=.purr.*;MeqTree logs=meqtree.log;Python files=*.py*;Backup files=*~,*.bck");
    self._ignore = parse_pattern_list(ignore);
    self._ignore_patterns = sets.Set();
    for desc,patts in self._ignore:
      self._ignore_patterns.update(patts);
    dprint(1,"ignoring patterns",self._ignore_patterns);
    self._watching = False;
    # create a timer
    if not self._timer:
      self._timer = QTimer(self);
      self.connect(self._timer,SIGNAL("timeout()"),self._rescan);
    
  def mainwin (self):
    return self._mainwin;
  
  def close (self):
    self.mainwin().close();
    # delete main window
    dum = QWidget();
    self.mainwin().reparent(dum,0,QPoint());
  
  def loadDirectory (self,dirname):
    """Attaches Purr to a directory (typically, an MS), and loads content""";
    dprint(1,"attaching to directory",dirname);
    self.dirname = dirname;
    self.logdir = os.path.join(dirname,"purr");
    self.title = "Unnamed log";
    self.timestamp = self.last_scan_timestamp = time.time();
    # create directory if it doesn't exist
    # error will be thrown if this is not possible
    if not os.path.exists(self.logdir):
      os.mkdir(self.logdir);
      dprint(1,"created",self.logdir);
    self.indexfile = os.path.join(self.logdir,"index.html");
    if os.path.exists(self.indexfile):
      try:
        parser = Purr.Parsers.LogIndexParser();
        for line in file(self.indexfile):
          parser.feed(line);
        self.title = parser.title or self.title;
        self.timestamp = parser.timestamp or self.timestamp;
        dprintf(2,"attached log '%s', timestamp %s\n",
                  self.title,time.strftime("%x %X",time.localtime(self.timestamp)));
      except:
        traceback.print_exc();
        print "Error parsing %s, reverting to defaults"%self.indexfile;
    # load log entries
    entries = [];
    for fname in os.listdir(self.logdir):
      pathname = os.path.join(self.logdir,fname);
      if Purr.LogEntry.isValidPathname(pathname):
        try:
          entry = Purr.LogEntry(load=pathname);
        except:
          print "Error loading entry %s, skipping"%fname;
          traceback.print_exc();
          continue;
        entries.append(entry);
      else:
        dprint(2,fname,"is not a valid Purr entry");
    # sort log entires by timestamp
    entries.sort(lambda a,b:cmp(a.timestamp,b.timestamp));
    self.setEntries(entries,save=False);
    # populate listview
    self.mainwin().setLogTitle(self.title);
    self.mainwin().setDirName(self.dirname,self.logdir);
  
  def setWatchedFiles (self,watch,ignore=[]):
    self._watch = watch;
    self._ignore = ignore;
    self._watch_patterns = sets.Set();
    for desc,patts in self._watch:
      self._watch_patterns.update(patts);
    dprint(1,"watching patterns",self._watch_patterns);
    self._ignore_patterns = sets.Set();
    for desc,patts in self._ignore:
      self._ignore_patterns.update(patts);
    dprint(1,"ignoring patterns",self._ignore_patterns);
    Config.set("watch-patterns",make_pattern_list(self._watch));
    Config.set("ignore-patterns",make_pattern_list(self._ignore));
    
  def watchDirectories (self,dirs):
    """Starts watching the specified directories for changes"""
    # collect timestamps of specified directories
    self._new_dps = sets.Set();
    for dirname in dirs:
      dirname = os.path.abspath(os.path.realpath(dirname));
      try:
        mtime = os.path.getmtime(dirname);
        fileset = sets.Set(os.listdir(dirname));
      except:
        print "Error accessing %s, will not be watched"%dirname;
        traceback.print_exc();
        continue;
      self._dir_timestamps[dirname] = self.timestamp,fileset;
      dprintf(2,"watching directory %s, mtime %s, %d files\n",
                 dirname,time.strftime("%x %X",time.localtime(mtime)),len(fileset));
      # generate list of files that have been created later than the timestamp, these will
      # be added to data products upon the next rescan
      if mtime > self.timestamp:
        dprintf(2,"%s modified since last run, checking for new files\n",dirname);
        for fname in fileset:
          # ignore files from ignore list
          if [ patt for patt in self._ignore_patterns if fnmatch.fnmatch(fname,patt) ]:
            dprintf(5,"%s: matches ignore list, skipping\n",fname);
            continue;
          fullname = os.path.join(dirname,fname);
          if os.path.isdir(fullname):
            continue;
          try:
            ctime = os.path.getctime(fullname);
          except:
            print "Error getting ctime for %s, ignoring"%fname;
            continue;
          if ctime > self.timestamp:
            dprintf(4,"%s: new data product (created %s)\n",
                    fullname,time.strftime("%x %X",time.localtime(ctime)));
            self._new_dps.add(fullname);
      # generate list of files to be watched for changes
      watchset = sets.Set();
      for patt in self._watch_patterns:
        watchset.update(fnmatch.filter(fileset,patt));
      for fname in watchset:
        fullname = os.path.join(dirname,fname);
        self._file_timestamps[fullname] = mtime = self.timestamp;
        dprintf(2,"watching file %s, timestamp %s\n",
                  fullname,time.strftime("%x %X",time.localtime(mtime)));
    # start watching
    self.enableWatching();
      
  def enableWatching (self,enable=True):
    if not self._watching and enable:
      self._rescan();
    self._watching = enable;
    if enable and (self._dir_timestamps or self._file_timestamps):
      self._timer.start(2000);
      dprintf(1,"starting timer\n");
    else:
      self._timer.stop();
      dprintf(1,"stopping timer\n");
      
  def setTitle (self,title):
    self.title = title;
    self.mainwin().setLogTitle(title);
    self.save();
  
  def newLogEntry (self,entry):
    """This is called when a new log entry is created""";
    self.entries.append(entry);
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
    try:
      entry.save(self.logdir);
      self.timestamp = self.last_scan_timestamp;
      self.save();
      self.updatePoliciesFromEntry(entry);
    finally:
      QApplication.restoreOverrideCursor();
      
  def updatePoliciesFromEntry (self,entry):
    # populate default policies and renames based on entry list
    for dp in entry.dps:
      # add default policy
      basename = os.path.basename(dp.orig_filename or dp.filename);
      self._default_dp_props[basename] = dp.policy,os.path.basename(dp.filename),dp.comment;
      # add files to watch lists
      if dp.policy != 'ignore':
        self._file_timestamps[dp.orig_filename] = dp.timestamp;
        dprintf(4,"watching file %s, timestamp %s\n",
                  dp.orig_filename,time.strftime("%x %X",time.localtime(dp.timestamp)));
  
  def save (self):
    outfile = file(self.indexfile,"wt");
    Purr.Parsers.writeLogIndex(outfile,self.title,self.timestamp,self.entries);
    # now go through data products, and update our timestamp maps
      
  def _editLogEntry (self):
    pass;
  
  def setEntries (self,entries,save=True):
    self.entries = entries;
    self.mainwin().setEntries(self.entries);
    if save:
      QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
      try: 
        self.save();
      finally:
        QApplication.restoreOverrideCursor();
    # populate default policies and renames based on entry list
    self._default_dp_props = {};
    for entry in entries:
      self.updatePoliciesFromEntry(entry);
    dprint(4,"default policies:",self._default_dp_props);
      
  def _rescan (self):
    """Checks files and directories on watchlist for updates, rescans them for new data products""";
    dprint(5,"starting rescan");
    newstuff = sets.Set();   # this accumulates names of new or changed files
    if self._new_dps:
      dprintf(2,"%d data products detected since last run\n",len(self._new_dps));
      newstuff.update(self._new_dps);
      self._new_dps = None;
    # store timestamp of scan
    self.last_scan_timestamp = time.time();
    # go through watched directories, check for mtime changes
    for dirname,(mtime,fileset) in list(self._dir_timestamps.iteritems()):
      try:
        mtime1 = os.path.getmtime(dirname);
      except:
        print "Error accessing %s, will no longer be watched"%dirname;
        traceback.print_exc();
        del self._dir_timestamps[dirname];
        continue;
      # no changes to directory? Continue
      if mtime1 <= mtime:
        dprintf(5,"directory %s: no change to mtime\n",dirname);
        continue;
      # get new file listing
      try:
        fileset1 = sets.Set(os.listdir(dirname));
      except:
        print "Error accessing %s, will no longer be watched"%dirname;
        traceback.print_exc();
        del self._dir_timestamps[dirname];
        continue;
      # go through new files
      newfiles = fileset1.difference(fileset);
      dprintf(3,"directory %s: %d new files\n",dirname,len(newfiles));
      for newfile in newfiles:
        # ignore directories
        if os.path.isdir(newfile):
          dprintf(5,"%s: is a directory, skipping\n",newfile);
          continue;
        # ignore files from ignore list
        if [ patt for patt in self._ignore_patterns if fnmatch.fnmatch(newfile,patt) ]:
          dprintf(5,"%s: matches ignore list, skipping\n",newfile);
          continue;
        # add file to list of new products
        fullname = os.path.abspath(os.path.realpath(os.path.join(dirname,newfile)));
        newstuff.add(os.path.join(dirname,newfile));
        dprintf(4,"%s: new data product\n",newfile);
      # reset timestamp and fileset
      self._dir_timestamps[dirname] = mtime1,fileset1;
    # now go through watched files, check for mtime changes
    for filename,mtime in list(self._file_timestamps.iteritems()):
      if not os.path.exists(filename):
        dprintf(4,"%s no longer exists, will stop watching\n",filename);
        del self._file_timestamps[filename];
        continue;
      try:
        mtime1 = os.path.getmtime(filename);
      except:
        print "Error accessing %s, will no longer be watched"%filename;
        traceback.print_exc();
        del self._file_timestamps[filename];
        continue;
      # no changes to file? Continue
      if mtime1 <= mtime:
        dprintf(5,"file %s: no change to mtime\n",filename);
        continue;
      # else add to data products
      dprintf(4,"%s: new data product\n",filename);
      newstuff.add(filename);
      self._file_timestamps[filename] = mtime1;
    # if we have new data products, send them to the main window
    dps = [];
    for filename in newstuff:
      basename = os.path.basename(filename);
      policy,rename,comment = self._default_dp_props.get(basename,("copy",None,""));
      dprintf(4,"%s: default policy is %s,%s,%s\n",basename,policy,rename,comment);
      dps.append(Purr.DataProduct(filename,policy=policy,rename=rename,comment=comment));
    self.mainwin().newDataProducts(dps);

  _running_purr = None;
  
  def run (parent,dirname):
    """Runs Purr as a slave of the given widget""";
    # Find out if Purr is already running on this dirname.
    # We can't use global variables for this, since (if we're called from within TDL) 
    # everything gets re-imported by TDL, so investigate parent instead.
    purr = Purrer._running_purr;
    if purr:
      if purr.dirname == dirname:
        dprint(1,"already running Purr on",dirname,"showing windows");
        purr.mainwin().show();
        return purr;
      dprint(1,"Purr running on",purr.dirname,"closing");
      purr.close();
      Purrer._running_purr = None;
    
    dirnames = [ dirname,'.' ];
  
    dprint(1,"Starting new Purr on",dirname);
    purr = Purrer._running_purr = Purrer(parent,dirnames[0],hide_on_close=True);
    purr.mainwin().show();  
    purr.watchDirectories(dirnames);
    
    return purr;

  run = staticmethod(run);