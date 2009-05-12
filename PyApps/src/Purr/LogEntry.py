import sys
import os
import time
import os.path
import re
import sets

import Purr
from Purr import dprint,dprintf
import Purr.Render

class DataProduct (object):
  def __init__ (self,filename=None,sourcepath=None,fullpath=None,
      policy="copy",comment="",
      timestamp=None,render=None,
      quiet=False,archived=False):
    # This is the absolute pathname to the original data product
    self.sourcepath = Purr.canonizePath(sourcepath);
    # Base filename (w/o path) of data product within the log storage area.
    # Products may be renamed when they are moved or copied over to the log.
    self.filename = filename or (sourcepath and os.path.basename(sourcepath));
    # Full path to the DP within the log storage area.
    # This is None until a DP has been saved.
    self.fullpath = fullpath;
    # Handling policy for DP: "copy","move","ignore", etc.
    self.policy = policy;
    # Comment associated with DP
    self.comment = comment;
    # Once a DP has been saved, this is the timestamp of data product at time of copy
    self.timestamp = timestamp;
    # Name of renderer used to render this DP.
    self.render = render;
    # if True, DP is watched quietly (i.e. Purr does not pop up windows on update)
    self.quiet = quiet;
    # if True, DP has already been archived. This is False for new DPs until they're saved.
    self.archived = archived;
    # if True, dp is ignored (policy is "ignore" or "banish")
    # not that policy should not be changed after a DP has been created
    self.ignored = policy in ("ignore","banish");
  
  def set_policy (self,policy):
    if self.archived:
      raise TypeError,"cannot change policy of archived DP";
    self.policy = policy;
    self.ignored = policy in ("ignore","banish");
  
  def subproduct_dir (self):
    """Returns name of subdirectory used to store subproducts of this data product
    during rendering.""";
    return self.fullpath+".purr-products";
  
  def remove_file (self):
    """Removes archived file associated with this DP""";
    if not self.fullpath or not self.archived:
      raise RuntimeError,"""Can't remove a non-archived data product""";
    try: 
      os.remove(self.fullpath);
    except:
      print "Error removing %s: %s"%(self.fullpath,sys.exc_info()[1]);

  def remove_subproducts (self):
    """Removes all archived files subproducts associated with this DP""";
    if not self.fullpath or not self.archived:
      raise RuntimeError,"""Can't remove a non-archived data product""";
    for root, dirs, files in os.walk(self.subproduct_dir(),topdown=False):
      for name in files:
        try: 
          os.remove(os.path.join(root, name)); 
        except: 
          pass;
      for name in dirs:
        try: 
          os.remove(os.path.join(root, name)); 
        except: 
          pass;
      
  def rename (self,newname):
    # rename file if needed
    if newname == self.filename:
      return;
    if not self.fullpath or not self.archived:
      raise RuntimeError,"""Can't rename a non-archived data product""";
    dirname = os.path.dirname(self.fullpath);
    newpath = os.path.join(dirname,newname);
    oldsubname = self.subproduct_dir();
    try:
      os.rename(self.fullpath,newpath);
    except:
      print "Error renaming %s to %s: %s"%(self.fullpath,newpath,sys.exc_info()[1]);
      return;
    # remove subproducts, if they exist -- need to re-render with new name anyway
    self.remove_subproducts();
    # set new paths and names
    self.fullpath = newpath;
    self.filename = newname;
    
  def restore_from_archive (self,parent=None):
    """Function to restore a DP from archived copy
    Asks for confirmation along the way if parent is not None
    (in which case it will be the parent widget for confirmation dialogs)
    """;
    from qt import QMessageBox;
    exists = os.path.exists(self.sourcepath);
    if parent:
      msg = """<P>Do you really want to restore <tt>%s</tt> from 
            this entry's archived copy of <tt>%s</tt>?</P>"""%(self.sourcepath,self.filename);
      exists = os.path.exists(self.sourcepath);
      if exists:
        msg += """<P>Current file exists, and will be overwritten.</P>""";
        if QMessageBox.warning(parent,"Restoring from archive",msg,
            QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
          return False;
      else:
        if QMessageBox.question(parent,"Restoring from archive",msg,
            QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
          return False;
    busy = Purr.BusyIndicator();
    # remove file if in the way
    if exists:
      if os.system("/bin/rm -fr %s"%self.sourcepath):
        busy = None;
        if parent:
          QMessageBox.warning(parent,"Error removing file","""<P>
            There was an error removing %s. Archived copy was not restored. 
            The text console may have more information.</P>"""%self.sourcepath,
            QMessageBox.Ok);
        return False;
    # copy over archived file
    if os.system("/bin/cp -a %s %s"%(self.fullpath,self.sourcepath)):
      busy = None;
      if parent:
        QMessageBox.warning(parent,"Error copying file","""<P>
          There was an error copying the archived version to %s. The text console may have more information.</P>"""%self.sourcepath,
          QMessageBox.Ok);
      return False;
    busy = None;
    if parent:
      QMessageBox.information(parent,"Restored file","""<P>Restored %s from this entry's 
          archived copy.</P>"""%self.sourcepath,
        QMessageBox.Ok);
    return True;

class LogEntry (object):
  """This represents a LogEntry object""";
  def __init__ (self,timestamp=None,title="",comment="",dps=[],load=None,ignore=False):
    self.title,self.comment,self.dps = title,comment,dps;
    self.timestamp = timestamp or int(time.time());
    self.pathname = None;
    self.ignore = ignore;
    # This is None for unsaved entries, and the pathname of the index.html file once
    # the entry is saved.
    # If the entry is edited, this is reset to None again.
    self.index_file = None;
    # This file caches HTML code for inclusion into a top-level log index.
    self.cached_include = None;
    # This is true if the cache is valid and up-to-date
    self.cached_include_valid = False;
    # This is true if entry is updated and needs to be saved. Set to False in load(),
    # set to True when something changes, or if load() detects that renderers have been updated.
    self.updated = True;
    if load:
      self.load(load);
    
  _entry_re = re.compile(".*/(entry|ignore)-(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)$");
  
  def isValidPathname (name):
    return os.path.isdir(name) and LogEntry._entry_re.match(name);
  isValidPathname = staticmethod(isValidPathname);
  
  def update (self,title=None,comment=None,dps=None,timestamp=None):
    self.updated = True;
    if title is not None:
      self.title = title;
    if comment is not None:
      self.comment = comment;
    if dps is not None:
      self.dps = dps;
    if timestamp is not None:
      self.timestamp = timestamp;
  
  def load (self,pathname):
    """Loads entry from directory.""";
    match = self. _entry_re.match(pathname);
    if not match:
      return None;
    self.ignore = (match.group(1) == "ignore");
    if not os.path.isdir(pathname):
      raise ValueError,"%s: not a directory"%pathname;
    if not os.access(pathname,os.R_OK|os.W_OK):
      raise ValueError,"%s: insufficient access privileges"%pathname;
    # parse index.html file
    parser = Purr.Parsers.LogEntryIndexParser(pathname);
    self.index_file = os.path.join(pathname,'index.html');
    for i,line in enumerate(file(self.index_file)):
      try:
        parser.feed(line);
      except:
        dprintf(0,"parse error at line %d of %s\n",i,self.index_file);
        raise;
    # set things up from parser
    try:
      self.timestamp = int(float(parser.timestamp));
    except:
      self.timestamp = int(time.time());
    self.title = getattr(parser,'title',None);
    if self.title is None:
      self.title = "Malformed entry, probably needs to be deleted";
    self.comment = getattr(parser,'comments',None) or "";
    self.dps = getattr(parser,'dps',[]);
    self.pathname = pathname;
    # see if any data products have been removed on us
    self.dps = [ dp for dp in self.dps if os.path.exists(dp.fullpath) ];
    # see if the cached include file is up-to-date
    self.cached_include = cache = os.path.join(pathname,'index.include.html');
    mtime = (os.path.exists(cache) or 0) and os.path.getmtime(cache);
    if mtime >= max(Purr.Render.youngest_renderer,os.path.getmtime(self.index_file)):
      dprintf(2,"entry %s has a valid include cache\n",pathname);
      self.cached_include_valid = True;
    else:
      dprintf(2,"entry %s does not have a valid include cache\n",pathname);
      self.cached_include_valid = False;
    # mark entry as unchanged, if renderers are older than index
    self.updated = (Purr.Render.youngest_renderer > os.path.getmtime(self.index_file));
      
  def save (self,dirname=None,refresh=False):
    """Saves entry in the given directory. Data products will be copied over if not
    residing in that directory.
    If refresh=True, all caches will be ignored and everything will be rerendered from scratch.
    """;
    if not refresh and not self.updated:
      return;
    if dirname:
      self.pathname = pathname = os.path.join(dirname,
                        ((self.ignore and "ignore") or "entry")+
                        time.strftime("-%Y%m%d-%H%M%S",
                                      time.localtime(self.timestamp)));
    elif not self.pathname:
      raise ValueError,"Cannot save entry: pathname not specified";
    else:
      pathname = self.pathname;
    # set timestamp
    if not self.timestamp:
      self.timestamp = int(time.time());
    # get canonized path to output directory
    pathname = Purr.canonizePath(pathname);
    # now save content
    if not os.path.exists(pathname):
      os.mkdir(pathname);
    # get device of pathname -- need to know whether we move or copy
    devnum = os.stat(pathname).st_dev;
    # copy data products as needed
    dps = [];
    for dp in self.dps:
      # if archived, this indicates a previously saved data product, so ignore it
      # if ignored, no need to save the DP -- but keep it in list
      if dp.archived or dp.ignored:
        dps.append(dp);
        continue;
      # file missing for some reason (perhaps it got removed on us?) skip data product entirely
      if not os.path.exists(dp.sourcepath):
        dprintf(2,"data product %s missing, ignoring\n",dp.sourcepath);
        continue;
      Purr.progressMessage("archiving %s"%dp.filename,sub=True);
      # get normalized source and destination paths
      dprintf(2,"data product: %s, rename %s, policy %s\n",dp.sourcepath,dp.filename,dp.policy);
      sourcepath = Purr.canonizePath(dp.sourcepath);
      destname = dp.fullpath = os.path.join(pathname,dp.filename);
      dprintf(2,"data product: %s -> %s\n",sourcepath,destname);
      # does the destination product already exist? skip if same file, else remove
      if os.path.exists(destname):
        if os.path.samefile(destname,sourcepath):
          dprintf(2,"same file, skipping\n");
          dp.timestamp = os.path.getmtime(destname);
          dps.append(dp);
          continue;
        if os.system("/bin/rm -fr %s"%destname):
          print "Error removing %s, which is in the way of %s"%(destname,sourcepath);
          print "This data product is not saved.";
          continue;
      # now copy/move it over
      if dp.policy == "copy":
        dprintf(2,"copying\n");
        if os.system("/bin/cp -ua %s %s"%(sourcepath,destname)):
          print "Error copying %s to %s"%(sourcepath,destname);
          print "This data product is not saved.";
          continue;
      elif dp.policy.startswith('move'):
        # files or directories on same device may be moved directly
        if not os.path.isdir(sourcepath) or os.stat(sourcepath).st_dev == devnum:
          dprintf(2,"same filesystem, moving\n");
          if os.system("/bin/mv -fu %s %s"%(sourcepath,destname)):
            print "Error moving %s to %s"%(sourcepath,destname);
            print "This data product is not saved.";
            continue;
        # else copy, then remove
        else:
          dprintf(2,"different filesystem, copying & removing\n");
          if os.system("/bin/mv -fu %s %s"%(sourcepath,destname)):
            print "Error moving %s to %s"%(sourcepath,destname);
            print "This data product is not saved.";
            continue;
          os.system("/bin/rm -fr %s"%sourcepath);
      # success, set timestamp and append
      dp.timestamp = os.path.getmtime(destname);
      dp.archived = True;
      dps.append(dp);
    # reset list of data products
    self.dps = dps;
    # now write out content
    self.cached_include = os.path.join(pathname,'index.include.html');
    self.cached_include_valid = False;  # cache will need to be regenerated now
    self.index_file = os.path.join(pathname,"index.html");
    file(self.index_file,"wt").write(self.renderIndex(refresh=refresh));
    self.updated = False;
    
  def remove_directory (self):
    """Removes this entry's directory from disk""";
    if not self.pathname:
      return;
    if os.system("/bin/rm -fr %s"%self.pathname):
      print "Error removing %s";
    
  def timeLabel (self):
    return time.strftime("%x %X",time.localtime(self.timestamp));
   
  def renderIndex (self,relpath="",refresh=False):
    """Returns HTML index code for this entry.
    If relpath is empty, renders complete index.html file.
    If relpath is not empty, then index is being included into a top-level log, and
    relpath should be passed to all sub-renderers.
    In this case the entry may make use of its cached_include file, if that is valid.
    If refresh=True, all caches will be ignored and everything will be rerendered from scratch.
    """;
    # check if cache can be used
    if refresh:
      self.cached_include_valid = False;
    if relpath and self.cached_include_valid:
      try:
        dprintf(2,"using include cache %s\n",self.cached_include);
        return file(self.cached_include).read();
      except:
        print "Error reading cached include code from %s, will regenerate"%self.cached_include;
        self.cached_include_valid = False;
    # form up attributes for % operator
    attrs = dict(self.__dict__);
    attrs['timestr'] = time.strftime("%x %X",time.localtime(self.timestamp));
    attrs['relpath'] = relpath;
    html = "";
    # replace title and comments for ignored entries
    if self.ignore:
      attrs['title'] = "This is not a real log entry";
      attrs['comment'] = """This entry was saved by PURR because the user
      chose to ignore and/or banish some data products. PURR has stored this
      information here for its opwn internal and highly nefarious purposes. 
      This entry is will not appear in the log.""";
    # replace < and > in title and comments
    attrs['title'] = attrs['title'].replace("<","&lt;").replace(">","&gt;");
    # write header if asked
    if not relpath:
      html += """<HTML><BODY>
      <TITLE>%(title)s</TITLE>
      <H2><A CLASS="TITLE" TIMESTAMP=%(timestamp)d>%(title)s</A></H2>"""%attrs;
    else:
      html += """
        <HR WIDTH=100%%>
        <H2>%(title)s</H2>"""%attrs;
    # write comments
    html += """
        <DIV ALIGN=right><P><SMALL>Logged on %(timestr)s</SMALL></P></DIV>\n
        
        <A CLASS="COMMENTS">\n"""%attrs;
    # add comments
    for cmt in self.comment.split("\n"):
      cmt = cmt.replace("<","&lt;").replace(">","&gt;");
      html += """      <P>%s</P>\n"""%cmt;
    html += """    </A>\n""";
    # add data products
    if self.dps:
      have_real_dps = bool([ dp for dp in self.dps if not dp.ignored ]);
      if have_real_dps:
        html += """
        <H3>Data products</H3>
        <TABLE BORDER=1 FRAME=box RULES=all CELLPADDING=5>\n""";
      for dp in self.dps:
        dpattrs = dict(dp.__dict__);
        dpattrs['comment'] = dpattrs['comment'].replace("<","&lt;").\
                        replace(">","&gt;").replace('"',"''");
        # if generating complete index, write empty anchor for each DP
        if not relpath:
          if dp.ignored:
            html += """
            <A CLASS="DP" SRC="%(sourcepath)s" POLICY="%(policy)s" COMMENT="%(comment)s"></A>\n"""%dpattrs;
          # write normal anchor for normal products
          else:
            dpattrs['relpath'] = relpath;
            dpattrs['basename'] = os.path.basename(dp.filename);
            html += """
            <A CLASS="DP" FILENAME="%(filename)s" SRC="%(sourcepath)s" POLICY="%(policy)s" QUIET=%(quiet)d TIMESTAMP=%(timestamp)d RENDER="%(render)s" COMMENT="%(comment)s"></A>\n"""%dpattrs;
        # render a table row
        if not dp.ignored:
          renderer = Purr.Render.makeRenderer(dp.render,dp,refresh=refresh);
          html += Purr.Render.renderInTable(renderer,relpath);
      if have_real_dps:
        html += """
        </TABLE>""";
    # write footer
    if not relpath:
      html += "</BODY></HTML>\n";
    else:
      # now, write to include cache, if being included
      file(self.cached_include,'w').write(html);
      self.cached_include_valid = True;
    return html;
      
