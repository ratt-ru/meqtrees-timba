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
  

class Purrer (object):
  def __init__ (self,dirname,watchdirs=None):
    # load and parse configuration
    # watched files
    watch = Config.get("watch-patterns","Images=*fits,*FITS");
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
    self._dir_timestamps  = {};
    self._file_timestamps = {};
    self._new_dps = sets.Set();
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
    
  def isIgnored (self,filename):
    return bool([ patt for patt in self._ignore_patterns if fnmatch.fnmatch(filename,patt) ]);
    
  def isQuiet (self,filename):
    return bool([ patt for patt in self._quiet_patterns if fnmatch.fnmatch(filename,patt) ]);
    
  def watchDirectories (self,dirs):
    """Starts watching the specified directories for changes"""
    # see if we're alredy watching this exact set of directories -- do nothing if so
    newset = sets.Set([Purr.canonizePath(dd) for dd in dirs]);
    if newset == sets.Set(self.watched_dirs):
      dprint(1,"watchDirectories: no change to set of dirs");
      return;
    # collect timestamps of specified directories
    self.watched_dirs = [];
    self._new_dps = sets.Set();
    for dirname in dirs:
      dirname = Purr.canonizePath(dirname);
      try:
        mtime = os.path.getmtime(dirname);
        fileset = sets.Set(os.listdir(dirname));
      except:
        print "Error accessing %s, will not be watched"%dirname;
        traceback.print_exc();
        continue;
      self.watched_dirs.append(dirname);
      self._dir_timestamps[dirname] = self.timestamp,fileset;
      dprintf(2,"watching directory %s, mtime %s, %d files\n",
                 dirname,time.strftime("%x %X",time.localtime(mtime)),len(fileset));
      # generate list of files that have been created later than the timestamp, these will
      # be added to data products upon the next rescan
      if mtime > self.timestamp:
        dprintf(2,"%s modified since last run, checking for new files\n",dirname);
        for fname in fileset:
          # ignore files from ignore list
          if self.isIgnored(fname):
            dprintf(5,"%s: matches ignore list, skipping\n",fname);
            continue;
          # see if it's in the quiet set
          quiet = self.isQuiet(fname);
          fullname = os.path.join(dirname,fname);
          if os.path.isdir(fullname):
            continue;
          try:
            ctime = os.path.getctime(fullname);
          except:
            print "Error getting ctime for %s, ignoring"%fname;
            continue;
          if ctime > self.timestamp:
            dprintf(4,"%s: new data product (created %s), quiet=%d\n",
                    fullname,time.strftime("%x %X",time.localtime(ctime)),quiet);
            self._new_dps.add((fullname,quiet));
      # generate list of files to be watched for changes
      watchset = sets.Set();
      for patt in self._watch_patterns:
        watchset.update(fnmatch.filter(fileset,patt));
      for fname in watchset:
        fullname = os.path.join(dirname,fname);
        quiet = self.isQuiet(os.path.basename(fname));
        self._file_timestamps[fullname] = self.timestamp,quiet;
        dprintf(2,"watching file %s, timestamp %s, quiet %d\n",
                  fullname,time.strftime("%x %X",time.localtime(self.timestamp)),quiet);
      
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
      # add files to watch lists
      if dp.policy != 'ignore':
        # if adding new file, quiet flag will be from dp
        # for old files, quiet flag is preserved
        mtime,quiet = self._file_timestamps.get(dp.sourcepath,(None,dp.quiet));
        self._file_timestamps[dp.sourcepath] = dp.timestamp,quiet;
        dprintf(4,"watching file %s, timestamp %s\n",
                  dp.sourcepath,time.strftime("%x %X",time.localtime(dp.timestamp)));
  
  def save (self):
    # create directory if it doesn't exist
    # error will be thrown if this is not possible
    _busy = Purr.BusyIndicator();
    if not os.path.exists(self.logdir):
      os.mkdir(self.logdir);
      dprint(1,"created",self.logdir);
    outfile = file(self.indexfile,"wt");
    Purr.progressMessage("Generating %s"%self.indexfile);
    Purr.Parsers.writeLogIndex(outfile,self.logtitle,self.timestamp,self.entries);
    Purr.progressMessage("Wrote %s"%self.indexfile);
      
  def rescan (self):
    """Checks files and directories on watchlist for updates, rescans them for new data products.
    If any are found, returns them.
    """;
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
        in_watchlist = [ patt for patt in self._watch_patterns if fnmatch.fnmatch(newfile,patt) ];
        # ignore files not matching watchlist, but matching ignore list
        if not in_watchlist and self.isIgnored(newfile):
          dprintf(5,"%s: matches ignore list, skipping\n",newfile);
          continue;
        # add file to list of new products
        quiet = self.isQuiet(newfile);
        newstuff.add((os.path.join(dirname,newfile),quiet));
        dprintf(4,"%s: new data product, quiet=%d\n",newfile,quiet);
      # reset timestamp and fileset
      self._dir_timestamps[dirname] = mtime1,fileset1;
    # now go through watched files, check for mtime changes
    for filename,(mtime,quiet) in list(self._file_timestamps.iteritems()):
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
      dprintf(4,"%s: new data product, quiet=%d\n",filename,quiet);
      newstuff.add((filename,quiet));
      self._file_timestamps[filename] = mtime1,quiet;
    # if we have new data products, send them to the main window
    return self.makeDataProducts(*newstuff);

  def makeDataProducts (self,*files):
    """makes a list of DPs from a list of (filename,quiet) pairs""";
    dps = [];
    for filename,quiet in files:
      sourcepath = Purr.canonizePath(filename);
      filename = os.path.basename(filename);
      policy,filename,comment = self._default_dp_props.get(filename,("copy",filename,""));
      dprintf(4,"%s: default policy is %s,%s,%s\n",sourcepath,policy,filename,comment);
      dps.append(Purr.DataProduct(filename=filename,sourcepath=sourcepath,
                                  policy=policy,comment=comment,quiet=quiet));
    return dps;

