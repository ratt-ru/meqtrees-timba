_tdl_no_reimport = True;

# TODO:
# - changing an MEP table while Purr is away does not case it to be pounced on upon
#   restart
# - add option to copy a DP from the archive
# - add a "banish" policy: stop pouncing
# - think of including verbatim code snippets in HTML

import sys
import os
import os.path
import re
import time
import traceback
import fnmatch
import sets
import signal

import Purr
import Purr.Parsers
import Purr.Render
import Purr.Plugins
from Purr import Config,dprint,dprintf;

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
  
def _printexc (message,*args):
  print message%args;
  traceback.print_exc();
    
def matches_patterns (filename,patterns):
  return bool([ patt for patt in patterns if fnmatch.fnmatch(filename,patt) ]);

class Purrer (object):
  class WatchedFile (object):
    """A WatchedFile represents a single file being watched for changes."""
    def __init__ (self,path,quiet=None,mtime=None):
      """Creates watched file at 'path'. The 'quiet' flag is simply stored.
      If 'mtime' is not None, this will be the file's last-changed timestamp.
      If 'mtime' is None, it will use os.path.getmtime().
      """
      self.path = path;
      self.quiet = quiet;
      self.mtime = mtime or self.getmtime();
      
    def getmtime (self):
      """Returns the file's modification time.
      Returns None on access error."""
      try:
        return os.path.getmtime(self.path);
      except:
        _print_exc("Error doing getmtime(%s)"%self.path);
        traceback.print_exc();
        return None;
      
    def isUpdated (self):
      """Checks if file was updated (i.e. mtime changed) since last check. Returns True if so.
      Returns None on access error."""
      mtime = self.getmtime();
      if mtime is None:
        return None;
      updated = (mtime or 0) > (self.mtime or 0);
      self.mtime = mtime;
      return updated;
    
    def newFiles (self):
      """Checks if there are any new files, returns iterable of (full) paths.
      (For a single file, this is just the file itself, if it has been updated.)
      Returns None on access error."""
      updated = self.isUpdated();
      if updated is None:
        return None;
      return (updated and [self.path]) or [];
    
  class WatchedDir (WatchedFile):
    """A WatchedDir represents a directory being watched for new files.
    """
    def __init__(self,path,watch_patterns=[],ignore_patterns=[],**kw):
      """Initializes directory. 
      'ignore_patterns' is a list of patterns to be ignored. 
      'watch_patterns' is a list of patterns to be watched.
      New files will be reported only if they don't match any of the ignore patterns, or
      match a watch pattern.
      All other arguments as per WatchedFile
      """;
      Purrer.WatchedFile.__init__(self,path,**kw);
      self.watch_patterns = watch_patterns;
      self.ignore_patterns = ignore_patterns;
      self._newfiles = [];
      # the self.fileset attribute gives the current directory content
      try:
        self.fileset = sets.Set(os.listdir(self.path));
      except:
        _print_exc("Error doing listdir(%s)"%self.path);
        traceback.print_exc();
        self.fileset = None;  # this indicates a read error
        return;
      # check for files created after the supplied timestamp
      if self.getmtime() > self.mtime:
        dprintf(2,"%s modified since last run, checking for new files\n",self.path);
        for fname in self.fileset:
          # ignore files from ignore list
          if matches_patterns(fname,ignore_patterns) and not matches_patterns(fname,watch_patterns):
            dprintf(5,"%s: matches ignore list but not watch list, skipping\n",fname);
            continue;
          fullname = os.path.join(self.path,fname);
          # check creation time against our timestamp
          try:
            ctime = os.path.getctime(fullname);
          except:
            _print_exc("Error getting ctime for %s, ignoring",fname);
            continue;
          if ctime > self.mtime:
            dprintf(4,"%s: new file (created %s)\n",fullname,
                      time.strftime("%x %X",time.localtime(ctime)));
            # append basename to _newfiles: full path added in newFiles() below
            self._newfiles.append(fname);
    
    def newFiles (self):
      """Returns new files (since last call to newFiles, or since creation).
      Return value is an iterable of (full) paths.
      Returns None on access error."""
      if self.fileset is None:
        return None;
      newfiles = sets.Set(self._newfiles);  # some newfiles may have been found in __init__
      self._newfiles = [];
      updated = self.isUpdated();
      if updated is None:
        return None;
      elif updated:
        try:
          fileset1 = sets.Set(os.listdir(self.path));
        except:
          _print_exc("Error doing listdir(%s)"%self.path);
          traceback.print_exc();
          self.fileset = None;
          return None;
        newfiles.update(fileset1.difference(self.fileset));
        self.fileset = fileset1;
      return [ os.path.join(self.path,filename) for filename in newfiles ];
    
  class WatchedSubdir (WatchedDir):
    """A WatchedSubdir represents a directory being watched for updates
    to specific files (called "canaries") within that directory. The directory itself 
    is reported as a "new file" if the directory mtime changes, or a canary has changed.
    """
    def __init__(self,path,canary_patterns=[],**kw):
      Purrer.WatchedDir.__init__(self,path,**kw);
      self.canary_patterns = canary_patterns;
      self.canaries = {};
      # if no read errors, make up list of canaries from canary patterns
      if self.fileset is not None:
        for fname in self.fileset:
          if matches_patterns(fname,canary_patterns):
            fullname = os.path.join(self.path,fname);
            self.canaries[fullname] = Purrer.WatchedFile(fullname,mtime=self.mtime);
            dprintf(3,"watching canary file %s, timestamp %s\n",
                      fullname,time.strftime("%x %X",time.localtime(self.mtime)));
      
    def newFiles (self):
      """Returns new files (since last call to newFiles, or since creation).
      The only possible new file is the subdirectory itself, which is considered
      new if updated, or if a canary has changed.
      Return value is an iterable, or None on access error.""" 
      # check directory itself for updates
      if self.fileset is None:
        return None;
      # check for new files first
      newfiles = Purrer.WatchedDir.newFiles(self);
      if newfiles is None:
        return None;
      # this timestamp is assigned to all canaries when directory has changed
      timestamp = time.time();
      canaries_updated = False;
      # check for new canaries among new files
      if newfiles:
        dprintf(3,"directory %s is updated\n",self.path);
        for fname in newfiles:
          if matches_patterns(os.path.basename(fname),self.canary_patterns):
            self.canaries[fname] = Purrer.WatchedFile(fname,mtime=timestamp);
            dprintf(3,"watching new canary file %s, timestamp %s\n",
                      fname,time.strftime("%x %X",time.localtime(timestamp)));
      # else check current canaries for updates
      else:
        for filename,watcher in list(self.canaries.iteritems()):
          updated = watcher.isUpdated();
          if updated is None:
            dprintf(2,"access error on canary %s, will no longer be watched",filename);
            del self.canaries[filename];
            continue;
          elif updated:
            dprintf(3,"canary %s is updated\n",filename);
            newfiles = True;  # this is treated as a bool below
            break;
        # now, if directory has updated, reset timestamps on all canaries
        if newfiles:
          for watcher in self.canaries.itervalues():
            watcher.mtime = timestamp;
      # returns ourselves (as new file) if something has updated
      return (newfiles and [self.path]) or [];
    
  def __init__ (self,dirname,watchdirs=None):
    # load and parse configuration
    # watched files
    watch = Config.get("watch-patterns","Images=*fits,*FITS,*jpg,*png;TDL configuration=.tdl.conf");
    self._watch = parse_pattern_list(watch);
    self._watch_patterns = sets.Set();
    for desc,patts in self._watch:
      self._watch_patterns.update(patts);
    dprint(1,"watching patterns",self._watch_patterns);
    # quietly watched files (dialog is not popped up)
    watch = Config.get("watch-patterns-quiet","TDL configuration=.tdl.conf");
    self._quiet = parse_pattern_list(watch);
    self._quiet_patterns = sets.Set();
    for desc,patts in self._quiet:
      self._quiet_patterns.update(patts);
    dprint(1,"quietly watching patterns",self._quiet_patterns);
    # merge into watch set 
    self._watch_patterns.update(self._quiet_patterns);
    # ignored files 
    ignore = Config.get("ignore-patterns","Hidden files=.*;MeqTree logs=meqtree.log;Python files=*.py*;Backup files=*~,*.bck");
    self._ignore = parse_pattern_list(ignore);
    self._ignore_patterns = sets.Set();
    for desc,patts in self._ignore:
      self._ignore_patterns.update(patts);
    dprint(1,"ignoring patterns",self._ignore_patterns);
    # watched subdirectories
    subdirs = Config.get("watch-subdirs","MEP tables=*mep/funklets,table.dat");
    _re_patt = re.compile("^(.*)=(.*)/(.*)$");
    self._subdir_patterns = [];
    for ss in subdirs.split(';'):
      match = _re_patt.match(ss);
      if match:
        desc = match.group(1);
        dir_patt = match.group(2).split(',');
        canary_patt = match.group(3).split(',');
        self._subdir_patterns.append((desc,dir_patt,canary_patt));
    dprint(1,"watching subdirectories",self._subdir_patterns);
    # attach to directories
    self._attach(dirname,watchdirs);
    
  def _attach (self,dirname,watchdirs=None):
    """Attaches Purr to a directory (typically, an MS), and loads content.
    Returns False if nothing new has been loaded (because directory is the same),
    or True otherwise.""";
    dirname = os.path.abspath(dirname);
    dprint(1,"attaching to directory",dirname);
    self.dirname = dirname;
    self.logdir = os.path.join(self.dirname,"purrlog");
    self.indexfile = os.path.join(self.logdir,"index.html");
    self.logtitle = "Unnamed log";
    self.timestamp = self.last_scan_timestamp = time.time();
    # reset internal state
    self.autopounce = False;
    self.watched_dirs = [];
    self.entries = [];
    self._default_dp_props = {};
    self.watchers = {};
    # load log state if log directory already exists
    if os.path.exists(self.logdir):
      _busy = Purr.BusyIndicator();
      if os.path.exists(self.indexfile):
        try:
          parser = Purr.Parsers.LogIndexParser();
          for line in file(self.indexfile):
            parser.feed(line);
          self.logtitle = parser.title or self.logtitle;
          self.timestamp = parser.timestamp or self.timestamp;
          dprintf(2,"attached log '%s', timestamp %s\n",
                    self.logtitle,time.strftime("%x %X",time.localtime(self.timestamp)));
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
            dprint(2,"loaded log entry",pathname);
          except:
            print "Error loading entry %s, skipping"%fname;
            traceback.print_exc();
            continue;
          entries.append(entry);
        else:
          dprint(2,fname,"is not a valid Purr entry");
      # sort log entires by timestamp
      entries.sort(lambda a,b:cmp(a.timestamp,b.timestamp));
      self.setLogEntries(entries,save=False);
    # start watching the specified directories
    if watchdirs is None:
      watchdirs = [dirname];
    self.watchDirectories(watchdirs);
  
  def setWatchedFilePatterns (self,watch,ignore=[]):
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
    # see if we're alredy watching this exact set of directories -- do nothing if so
    newset = sets.Set([Purr.canonizePath(dd) for dd in dirs]);
    if newset == sets.Set(self.watched_dirs):
      dprint(1,"watchDirectories: no change to set of dirs");
      return;
    # collect timestamps of specified directories
    self.watchers = {};
    for dirname in newset:
      wdir = Purrer.WatchedDir(dirname,mtime=self.timestamp,
              watch_patterns=self._watch_patterns,ignore_patterns=self._ignore_patterns);
      # fileset=None indicates error reading directory, so ignore it
      if wdir.fileset is None:
        continue;
      self.watchers[dirname] = wdir;
      self.watched_dirs.append(dirname);
      dprintf(2,"watching directory %s, mtime %s, %d files\n",
                 dirname,time.strftime("%x %X",time.localtime(wdir.mtime)),len(wdir.fileset));
      # find files in this directory matching the watch_patterns, and watch them for changes
      watchset = sets.Set();
      for patt in self._watch_patterns:
        watchset.update(fnmatch.filter(wdir.fileset,patt));
      for fname in watchset:
        quiet = matches_patterns(fname,self._quiet_patterns);
        fullname = Purr.canonizePath(os.path.join(dirname,fname));
        wfile = Purrer.WatchedFile(fullname,quiet=quiet,mtime=self.timestamp);
        self.watchers[fullname] = wfile;
        dprintf(3,"watching file %s, timestamp %s, quiet %d\n",
                  fullname,time.strftime("%x %X",time.localtime(wfile.mtime)),quiet);
      # find subdirectories  matching the subdir_patterns, and watch them for changes
      for fname in wdir.fileset:
        fullname = Purr.canonizePath(os.path.join(dirname,fname));
        if os.path.isdir(fullname):
          for desc,dir_patts,canary_patts in self._subdir_patterns:
            if matches_patterns(fname,dir_patts):
              quiet = matches_patterns(fname,self._quiet_patterns);
              wdir = Purrer.WatchedSubdir(fullname,canary_patterns=canary_patts,quiet=quiet,mtime=self.timestamp);
              self.watchers[fullname] = wdir;
              dprintf(3,"watching subdirectory %s/{%s}, timestamp %s, quiet %d\n",
                        fullname,",".join(canary_patts),time.strftime("%x %X",time.localtime(wdir.mtime)),quiet);
              break;
            
  def setLogTitle (self,title,save=True):
    self.logtitle = title;
    if save:
      self.save();
  
  def addLogEntry (self,entry,save=True):
    """This is called when a new log entry is created""";
    self.entries.append(entry);
    _busy = Purr.BusyIndicator();
    # create directory if it doesn't exist
    # error will be thrown if this is not possible
    if not os.path.exists(self.logdir):
      os.mkdir(self.logdir);
      dprint(1,"created",self.logdir);
    Purr.progressMessage("Saving new log entry");
    entry.save(self.logdir);
    self.timestamp = self.last_scan_timestamp;
    if save:
      self.save();
    self.updatePoliciesFromEntry(entry);
      
  def getLogEntries (self):
    return self.entries;
      
  def setLogEntries (self,entries,save=True):
    self.entries = entries;
    if save:
      self.save();
    # populate default policies and renames based on entry list
    self._default_dp_props = {};
    for entry in entries:
      self.updatePoliciesFromEntry(entry);
    dprint(4,"default policies:",self._default_dp_props);
      
  def updatePoliciesFromEntry (self,entry):
    # populate default policies and renames based on entry list
    for dp in entry.dps:
      # add default policy
      basename = os.path.basename(dp.sourcepath);
      self._default_dp_props[basename] = dp.policy,dp.filename,dp.comment;
      # make new watchers for non-ignored files
      if dp.policy != 'ignore' and dp.sourcepath not in self.watchers:
        wfile = Purrer.WatchedFile(dp.sourcepath,quiet=dp.quiet,mtime=dp.timestamp);
        self.watchers[dp.sourcepath] = wfile;
        dprintf(4,"watching file %s, timestamp %s\n",
                  dp.sourcepath,time.strftime("%x %X",time.localtime(dp.timestamp)));
  
  def save (self,refresh=False):
    """Saves the log.
    If 'refresh' is True, it will ignore all cached documents and regenerate the log from
    scratch.
    """;
    # create directory if it doesn't exist
    # error will be thrown if this is not possible
    _busy = Purr.BusyIndicator();
    if not os.path.exists(self.logdir):
      os.mkdir(self.logdir);
      dprint(1,"created",self.logdir);
    outfile = file(self.indexfile,"wt");
    Purr.progressMessage("Generating %s"%self.indexfile);
    # if refresh is True, re-save all entries. This will clear all caches
    if refresh:
      for entry in self.entries:
        entry.save(refresh=True);
    Purr.Parsers.writeLogIndex(outfile,self.logtitle,self.timestamp,self.entries);
    Purr.progressMessage("Wrote %s"%self.indexfile);
    
  def rescan (self):
    """Checks files and directories on watchlist for updates, rescans them for new data products.
    If any are found, returns them.
    """;
    dprint(5,"starting rescan");
    newstuff = {};   # this accumulates names of new or changed files. Keys are paths, values are 'quiet' flag.
    # store timestamp of scan
    self.last_scan_timestamp = time.time();
    # go through watched directories, check for mtime changes
    for path,watcher in list(self.watchers.iteritems()):
      # get list of new files from watcher
      newfiles = watcher.newFiles();
      # None indicates access error, so drop it from watcher set
      if newfiles is None:  
        dprintf(2,"access error on %s, will no longer be watched",watcher.path);
        del self.watchers[path];
        continue;
      dprintf(5,"%s: %d new file(s)\n",watcher.path,len(newfiles));
      # Now go through files and add them to the newstuff dict
      for newfile in newfiles:
        # if quiet flag is explicitly set on watcher, use it, else compare filename to quiet patterns
        quiet = watcher.quiet;
        if quiet is None:
          quiet = matches_patterns(os.path.basename(newfile),self._quiet_patterns);
        # add file to list of new products. Since a file may be reported by multiple
        # watchers, make the quiet flag a logical AND of all the quiet flags (i.e. DP will be
        # marked as quiet only if all watchers report it as quiet).
        newstuff[newfile] = quiet and newstuff.get(newfile,False);
        dprintf(4,"%s: new data product, quiet=%d\n",newfile,quiet);
    # if we have new data products, send them to the main window
    return self.makeDataProducts(*newstuff.iteritems());
          

  def makeDataProducts (self,*files):
    """makes a list of DPs from a list of (filename,quiet) pairs""";
    dps = [];
    for filename,quiet in files:
      filename = filename.rstrip('/');
      sourcepath = Purr.canonizePath(filename);
      filename = os.path.basename(filename);
      policy,filename,comment = self._default_dp_props.get(filename,("copy",filename,""));
      dprintf(4,"%s: default policy is %s,%s,%s\n",sourcepath,policy,filename,comment);
      dps.append(Purr.DataProduct(filename=filename,sourcepath=sourcepath,
                                  policy=policy,comment=comment,quiet=quiet));
    return dps;

