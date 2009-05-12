_tdl_no_reimport = True;

import os.path
import time

from qt import *

import Purr
import Purr.Editors
import Purr.LogEntry
import Purr.Pipe
from Purr import Config,pixmaps,dprint,dprintf


class BusyIndicator (object):
  def __init__ (self):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
  def __del__ (self):
    QApplication.restoreOverrideCursor();

class HTMLViewerDialog (QDialog):
  """This class implements a dialog to view a piece of HTML text.""";
  def __init__ (self,parent,config_name=None,buttons=[],*args):
    """Creates dialog.
    'config_name' is used to get/set default window size from Config object
    'buttons' can be a list of names or (QPixmapWrapper,name[,tooltip]) tuples to provide 
    custom buttons at the bottom of the dialog. When a button is clicked, the dialog 
    emits PYSIGNAL("name()").
    A "Close" button is always provided, this simply hides the dialog.
    """;
    QDialog.__init__(self,parent,*args);
    self.setModal(False);
    lo = QVBoxLayout(self);
    # create viewer
    self.label = QLabel(self);
    self.label.setMargin(5);
    lo.addWidget(self.label);
    self.label.hide();
    self.viewer = QTextEdit(self);
    lo.addWidget(self.viewer);
    self.viewer.setReadOnly(True);
    self.viewer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    # make a QMimeSourceFactory for the viewer -- needed to resolve image links
    self.viewer_msf = QMimeSourceFactory();
    self.viewer.setMimeSourceFactory(self.viewer_msf);
    lo.addSpacing(5);
    # create button bar
    btnfr = QFrame(self);
    btnfr.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    btnfr.setMargin(5);
    lo.addWidget(btnfr);
    lo.addSpacing(5);
    btnfr_lo = QHBoxLayout(btnfr);
    btnfr_lo.setMargin(5);
    # add user buttons
    self._user_buttons = {};
    for name in buttons:
      if isinstance(name,str):
        btn = QPushButton(name,btnfr);
      elif isinstance(name,(list,tuple)):
        if len(name) < 3:
          pixmap,name = name;
          tip = None;
        else:
          pixmap,name,tip = name;
        btn = QPushButton(pixmap.iconset(),name,btnfr);
        if tip:
          QToolTip.add(btn,tip);
      self._user_buttons[name] = btn;
      self.connect(btn,SIGNAL("clicked()"),self,PYSIGNAL(name+"()"));
      btnfr_lo.addWidget(btn,1);
    # add a Close button
    btnfr_lo.addStretch(100);
    closebtn = QPushButton(pixmaps.grey_round_cross.iconset(),"Close",btnfr);
    self.connect(closebtn,SIGNAL("clicked()"),self.hide);
    btnfr_lo.addWidget(closebtn,1);
    # resize selves
    self.config_name = config_name or "html-viewer";
    width = Config.getint('%s-width'%self.config_name,256);
    height = Config.getint('%s-height'%self.config_name,512);
    self.resize(QSize(width,height));
    
  def resizeEvent (self,ev):
    QDialog.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('%s-width'%self.config_name,sz.width());
    Config.set('%s-height'%self.config_name,sz.height());
    
  def setDocument (self,text,path='.'):
    """Sets the HTML text to be displayed. 'path' can be used to give a relative path for
    resolving images in the text""";
    self.viewer_msf.setFilePath(QStringList(path));
    self.viewer.setText(text);
    
  def setLabel (self,label=None):
    if label is None:
      self.label.hide();
    else:
      self.label.setText(label);
      self.label.show();

class MainWindow (QMainWindow):
  
  about_message = """
    <P>PURR ("<B>P</B>URR is <B>U</B>seful for <B>R</B>emembering <B>R</B>eductions", for those working with
    a stable version, or "<B>P</B>URR <B>U</B>sually <B>R</B>emembers <B>R</B>eductions", for those 
    working with a development version, or "<B>P</B>URR <B>U</B>sed to <B>R</B>emember <B>R</B>eductions", 
    for those working with a broken version) is a tool for
    automatically keeping a log of your data reduction operations. PURR will watch your working directories
    for new files (called "data products"), and upon seeing any, it can "pounce" -- that is, offer
    you the option of saving them to a log, along with descriptive comments. It will then
    generate an HTML page with a rendering of your log and data products.</P>
  """;
  
  pounce_help = \
      """<P>This control determines what PURR does about updated files.</P>
      
      <P>If <B>pounce & show</B> is selected, PURR will periodically check your working directories for new
      or updated files, and pop up the "New Log Entry" dialog when it detects any.</P>
      
      <P><B>Pounce</B> alone is less obtrusive. PURR will watch for files and quietly add them to the "New Log Entry" dialog, but will not display the dialog. You can display the dialog yourself by
      clicking on "New entry".</P>
      
      <P>If <B>ignore</B> is selected, PURR will not watch for changes at all. In this mode, you can use the "Rescan" button to check for new or updated files.</P>
      """;

  # constants for autopounce modes
  PounceIgnore = 0;
  PouncePounce = 1;
  PounceShow = 2;
  # labels for the pounce mode combobox
  pounce_labels = [ "ignore","pounce","pounce & show" ];
  
  def __init__ (self,parent,hide_on_close=False):
    QMainWindow.__init__(self,parent);
    self._hide_on_close = hide_on_close;
    # replace the BusyIndicator class with a GUI-aware one
    Purr.BusyIndicator = BusyIndicator;
    # autopounce is on if GUI checkbox is on
    # pounce is on if autopounce is on, or the new Entry dialog is visible.
    self._autopounce = self.PounceIgnore;
    self._pounce = False;
    # we keep a small stack of previously active purrers. This makes directory changes
    # faster (when going back and forth between dirs)
    # current purrer
    self.purrer = None;
    self.purrer_stack = [];
    # Purr pipe for receiving remote commands
    self.purrpipe = None;
    # init GUI
    self.setCaption("PURR");
    self.setIcon(pixmaps.purr_logo.pm());
    cw = QWidget(self);
    self.setCentralWidget(cw);
    cwlo = QVBoxLayout(cw);
    cwlo.setMargin(5);
    toplo = QHBoxLayout(cwlo);
    label = QLabel("Updated files:",cw);
    toplo.addWidget(label);
    toplo.addSpacing(5);
    self.wpounce = QComboBox(cw);
    QToolTip.add(self.wpounce,self.pounce_help);
    self.wpounce.insertStrList(self.pounce_labels);
    self.wpounce.setCurrentItem(self._autopounce);
    self.connect(self.wpounce,SIGNAL("activated(int)"),self.setPounceMode);
    toplo.addWidget(self.wpounce,1);
    toplo.addSpacing(5);
    wrescan = QPushButton(pixmaps.blue_round_reload.iconset(),"Rescan",cw);
    QToolTip.add(wrescan,"Checks your working directories for new or updated files.");
    self.connect(wrescan,SIGNAL("clicked()"),self._forceRescan);
    toplo.addWidget(wrescan);
    toplo.addStretch(1);
    about_btn = QPushButton("About...",cw);
    about_btn.setMinimumWidth(128);
    about_btn.setFlat(True);
    about_btn.setIconSet(pixmaps.purr_logo.iconset());
    toplo.addWidget(about_btn);
    self._about_dialog = QMessageBox("About PURR",self.about_message + """
        <P>PURR is not watching any directories right now. Click on the "pounce" option to start
        watching your current directory.</P>""",
        QMessageBox.NoIcon,
        QMessageBox.Ok,QMessageBox.NoButton,QMessageBox.NoButton,cw);
    self._about_dialog.setIconPixmap(pixmaps.purr_logo.pm()); 
    self.connect(about_btn,SIGNAL("clicked()"),self._about_dialog.exec_loop);
    cwlo.addSpacing(5);
    logframe = QFrame(cw);
    cwlo.addWidget(logframe);
    log_lo = QVBoxLayout(logframe);
    log_lo.setMargin(5);
    logframe.setFrameStyle(QFrame.Box|QFrame.Raised);
#    logframe.setFrameShape(QFrame.Panel);
    logframe.setLineWidth(1);
    self.dir_label = QLabel("Directory: none",logframe);
    log_lo.addWidget(self.dir_label);
    title_lo = QHBoxLayout(log_lo);
    self.title_label = QLabel("Log title: none",logframe);
    title_lo.addWidget(self.title_label,1);
    self.wrename = QPushButton("Rename",logframe);
    QToolTip.add(self.wrename,"Click to edit log title");
    self.wrename.setMinimumWidth(80);
    self.wrename.setFlat(True);
    self.wrename.setEnabled(False);
    self.connect(self.wrename,SIGNAL("clicked()"),self._renameLogDialog);
    title_lo.addWidget(self.wrename,0);
    title_lo.addSpacing(5);
    self.wviewlog = QPushButton(pixmaps.openbook.iconset(),"View",logframe);
    QToolTip.add(self.wviewlog,"Click to see an HTML rendering of the log");
    self.wviewlog.setMinimumWidth(80);
    self.wviewlog.setFlat(True);
    self.wviewlog.setEnabled(False);
    # log viewer dialog
    self.viewer_dialog = HTMLViewerDialog(self,config_name="log-viewer",
          buttons=[(pixmaps.blue_round_reload,"Regenerate",
                   """<P>Regenerates your log's HTML code from scratch. This can be useful if
                   your PURR version has changed, or if there was an error of some kind
                   the last time the files were generated.</P>
                   """)]);
    self._viewer_timestamp = None;
    self.connect(self.wviewlog,SIGNAL("clicked()"),self._showViewerDialog);
    self.connect(self.viewer_dialog,PYSIGNAL("Regenerate()"),self._regenerateLog);
    title_lo.addWidget(self.wviewlog,0);
    cwlo.addSpacing(5);
    # listview of log entries
    self.elv = QListView(cw);
    cwlo.addWidget(self.elv);
    self.elv.addColumn("date");
    self.elv.addColumn("entry title",128);
    self.elv.addColumn("comment",-1);
    self.elv.header().show();
    self.elv.setAllColumnsShowFocus(True);
    self.elv.setShowToolTips(True);
    self.elv.setSorting(-1);
    self.elv.setResizeMode(QListView.LastColumn);
    self.elv.setColumnAlignment(2,Qt.AlignLeft|Qt.AlignTop);
    self.elv.setSelectionMode(QListView.Extended);
    self.elv.setRootIsDecorated(True);
    self.connect(self.elv,SIGNAL("selectionChanged()"),self._entrySelectionChanged);
    self.connect(self.elv,SIGNAL("doubleClicked(QListViewItem*,const QPoint&,int)"),self._viewEntryItem);
    self.connect(self.elv,SIGNAL("returnPressed(QListViewItem*)"),self._viewEntryItem);
    self.connect(self.elv,SIGNAL("spacePressed(QListViewItem*)"),self._viewEntryItem);
    self.connect(self.elv,SIGNAL('contextMenuRequested(QListViewItem*,const QPoint &,int)'),
                     self._showItemContextMenu);
    # create popup menu for data product
    self._archived_dp_menu = menu = QPopupMenu(self);
    qa = QAction(pixmaps.editcopy.iconset(),"Restore file from this entry's archived copy",0,menu);
    QObject.connect(qa,SIGNAL("activated()"),self._restoreItemFromArchive);
    qa.addTo(self._archived_dp_menu);
    qa = QAction(pixmaps.editpaste.iconset(),"Copy location of archived copy to clipboard",0,menu);
    QObject.connect(qa,SIGNAL("activated()"),self._copyItemToClipboard);
    qa.addTo(self._archived_dp_menu);
    self._current_item = None;
    # buttons at bottom
    cwlo.addSpacing(5);
    btnlo = QHBoxLayout(cwlo);
    self.wnewbtn = QPushButton(pixmaps.filenew.iconset(),"New entry...",cw);
    QToolTip.add(self.wnewbtn,"Click to add a new log entry");
    self.wnewbtn.setFlat(True);
    self.wnewbtn.setEnabled(False);
    btnlo.addWidget(self.wnewbtn);
    btnlo.addSpacing(5);
    self.weditbtn = QPushButton(pixmaps.filefind.iconset(),"View entry...",cw);
    QToolTip.add(self.weditbtn,"Click to view or edit the selected log entry");
    self.weditbtn.setFlat(True);
    self.weditbtn.setEnabled(False);
    self.connect(self.weditbtn,SIGNAL("clicked()"),self._viewEntryItem);
    btnlo.addWidget(self.weditbtn);
    btnlo.addSpacing(5);
    self.wdelbtn = QPushButton(pixmaps.editdelete.iconset(),"Delete",cw);
    QToolTip.add(self.wdelbtn,"Click to delete the selected log entry or entries");
    self.wdelbtn.setFlat(True);
    self.wdelbtn.setEnabled(False);
    self.connect(self.wdelbtn,SIGNAL("clicked()"),self._deleteSelectedEntries);
    btnlo.addWidget(self.wdelbtn);
    # enable status line
    self.statusBar().show();
    Purr.progressMessage = self.message;
    self._prev_msg = None;
    # editor dialog for new entry
    self.new_entry_dialog = Purr.Editors.NewLogEntryDialog(self);
    self.connect(self.new_entry_dialog,PYSIGNAL("newLogEntry()"),self._newLogEntry);
    self.connect(self.new_entry_dialog,PYSIGNAL("filesSelected()"),self._addDPFiles);
    self.connect(self.wnewbtn,SIGNAL("clicked()"),self.new_entry_dialog.show);
    self.connect(self.new_entry_dialog,PYSIGNAL("shown()"),self._checkPounceStatus);
    # entry viewer dialog
    self.view_entry_dialog = Purr.Editors.ExistingLogEntryDialog(self);
    self.connect(self.view_entry_dialog,PYSIGNAL("previous()"),self._viewPrevEntry);
    self.connect(self.view_entry_dialog,PYSIGNAL("next()"),self._viewNextEntry);
    self.connect(self.view_entry_dialog,PYSIGNAL("filesSelected()"),self._addDPFilesToOldEntry);
    self.connect(self.view_entry_dialog,PYSIGNAL("entryChanged()"),self._entryChanged);
    # saving a data product to an older entry will automatically drop it from the
    # new entry dialog
    self.connect(self.view_entry_dialog,PYSIGNAL("creatingDataProduct()"),
                  self.new_entry_dialog.dropDataProducts);
    # resize selves
    width = Config.getint('main-window-width',512);
    height = Config.getint('main-window-height',512);
    self.resize(QSize(width,height));
    # create timer for pouncing
    self._timer = QTimer(self);
    self.connect(self._timer,SIGNAL("timeout()"),self._rescan);
    
  def resizeEvent (self,ev):
    QMainWindow.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('main-window-width',sz.width());
    Config.set('main-window-height',sz.height());
    
  def closeEvent (self,ev):
    if self._hide_on_close:
      ev.ignore();
      self.hide();
      self.new_entry_dialog.hide();
    else:
      if self.purrer:
        self.purrer.detach();
      return QMainWindow.closeEvent(self,ev);
    
  def message (self,msg,ms=2000,sub=False):
    if sub:
      if self._prev_msg:
        msg = ": ".join((self._prev_msg,msg));
    else:
      self._prev_msg = msg;
    self.statusBar().message(msg,ms);
    QApplication.eventLoop().processEvents(QEventLoop.ExcludeUserInput);
      
  def detachDirectory (self):
    self.purrer and self.purrer.detach();
    
  def attachDirectory (self,dirname,watchdirs=None):
    """Attaches Purr to the given directory. If watchdirs is None,
    the current directory will be watched, otherwise the given directories will be watched."""
    # check purrer stack for a Purrer already watching this directory
    dprint(1,"attaching to directory",dirname);
    for i,purrer in enumerate(self.purrer_stack):
      if os.path.samefile(purrer.dirname,dirname):
        dprint(1,"Purrer object found on stack (#%d),reusing\n",i);
        # found? move to front of stack
        self.purrer_stack.pop(i);
        self.purrer_stack.insert(0,purrer);
        # update purrer with watched directories, in case they have changed
        if watchdirs:
          purrer.watchDirectories(watchdirs);
        break;
    # no purrer found, make a new one
    else:
      dprint(1,"creating new Purrer object");
      try:
        purrer = Purr.Purrer(dirname,watchdirs or (dirname,));
      except Purr.Purrer.LockedError,err:
        # check that we could attach, display message if not
        QMessageBox.warning(self,"Catfight!","""<P><NOBR>It appears that another PURR process (%s)</NOBR>
          is already attached to <tt>%s</tt>, so we're not allowed to touch it. You should exit the other PURR
          process first.</P>"""%(err.args[0],os.path.abspath(dirname)),QMessageBox.Ok);
        return False;
      except Purr.Purrer.LockFailError,err:
        QMessageBox.warning(self,"Failed to lock directory","""<P><NOBR>PURR was unable to obtain a lock</NOBR>
          on directory <tt>%s</tt> (error was "%s"). The most likely cause is insufficient permissions.</P>"""%(os.path.abspath(dirname),err.args[0]),QMessageBox.Ok);
        return False;
      self.purrer_stack.insert(0,purrer);
      # discard end of stack
      self.purrer_stack = self.purrer_stack[:3];
      # attach signals
      self.connect(purrer,PYSIGNAL("disappearedFile()"),
                   self.new_entry_dialog.dropDataProducts);
      self.connect(purrer,PYSIGNAL("disappearedFile()"),
                   self.view_entry_dialog.dropDataProducts);
    # have we changed the current purrer? Update our state then
    # reopen pipe
    self.purrpipe = Purr.Pipe.open(purrer.dirname);
    if purrer is not self.purrer:
      self.message("Attached to directory %s"%purrer.dirname);
      dprint(1,"current Purrer changed, updating state");
      self.purrer = purrer;
      self.new_entry_dialog.hide();
      self.new_entry_dialog.reset();
      self.new_entry_dialog.setDefaultDirs(*purrer.watched_dirs);
      self.view_entry_dialog.setDefaultDirs(*purrer.watched_dirs);
      self.view_entry_dialog.hide();
      self._viewing_ientry = None;
      self._setEntries(self.purrer.getLogEntries());
      self._viewer_timestamp = None;
      self._updateViewer();
      self._updateNames();
      # set autopounce property from purrer. Reset _pounce to false -- this will cause
      # checkPounceStatus() into a rescan if autopounce is on.
      self.setPounceMode(purrer.autopounce);
      self._pounce = False;
      self._checkPounceStatus();
    return True;
    
  def setLogTitle (self,title):
    self.purrer.setLogTitle(title);
    self._updateNames();
    self._updateViewer();
    
  def setPounceMode (self,enable=PounceShow):
    enable = int(enable)%len(self.pounce_labels);
    if enable != self.PounceIgnore and not self.purrer:
      self.attachDirectory('.');
    self._autopounce = enable;
    if self.purrer:
      self.purrer.autopounce = enable;
    self.wpounce.setCurrentItem(enable%len(self.pounce_labels));
    self._checkPounceStatus();
    
  def _updateNames (self):
    self.wnewbtn.setEnabled(True);
    self.wrename.setEnabled(True);
    self.wviewlog.setEnabled(True);
    self._about_dialog.setText(self.about_message + """
    <P>Your current log resides in:<PRE>  <tt>%s</tt></PRE>To see your log in all its HTML-rendered glory, point your browser to <tt>index.html</tt> therein, or use the handy "View" button provided by PURR.</P>
    
    <P>Your current working directories are:</P>
    <P>%s</P>
    """%(self.purrer.logdir,
      "".join([ "<PRE>  <tt>%s</tt></PRE>"%name for name in self.purrer.watched_dirs ])
    ));
    self.dir_label.setText("Directory: %s"%self.purrer.dirname);
    title = self.purrer.logtitle or "Unnamed log"
    self.title_label.setText("Log title: <B>%s</B>"%title);
    self.viewer_dialog.setCaption(title);
    
  def _showViewerDialog (self):
    self._updateViewer(True);
    self.viewer_dialog.show();
    
  def _updateViewer (self,force=False):
    """Updates the viewer dialog.
    If dialog is not visible and force=False, does nothing.
    Otherwise, checks the mtime of the current purrer index.html file against self._viewer_timestamp.
    If it is newer, reloads it.
    """;
    if not force and not self.viewer_dialog.isVisible():
      return;
    # default text if nothing is found
    text = "<P>Nothing in the log yet. Try adding some entries first.</P>";
    try:
      mtime = os.path.getmtime(self.purrer.indexfile);
    except:
      mtime = None;
    # return if file is older than our content
    if mtime and mtime < (self._viewer_timestamp or 0):
      return;
    busy = BusyIndicator();
    try:
      text = file(self.purrer.indexfile).read();
    except:
      pass;
    self.viewer_dialog.setDocument(text,os.path.dirname(self.purrer.indexfile));
    self.viewer_dialog.setLabel("""<P>Below is your full HTML-rendered log. Note that this window 
      is only a bare-bones viewer, not a real browser. You can't
      click on links, or do anything else besides simply look. For a fully-functional view, use your
      browser to look at the index file residing here:<BR>
      <tt>%s</tt></P> 
      """%self.purrer.indexfile);
    self._viewer_timestamp = mtime;
    
  def _setEntries (self,entries):
    self.elv.clear();
    item = None;
    for i,entry in enumerate(entries):
      item = self._addEntryItem(entry,i,item);
      
  def _renameLogDialog (self):
    (title,ok) = QInputDialog.getText("PURR: Rename Log",
                  "Enter new name for this log",QLineEdit.Normal,self.purrer.logtitle,self);
    if ok and title != self.purrer.logtitle:
      self.setLogTitle(title);
      
  def _checkPounceStatus (self):
    pounce = self._autopounce != self.PounceIgnore or self.new_entry_dialog.isVisible();
    # rescan, if going from not-pounce to pounce
    if pounce and not self._pounce:
      self._rescan();
    self._pounce = pounce;
    # start timer -- we need it running to check the purr pipe, anyway
    self._timer.start(2000);
      
  def _forceRescan (self):
    self._rescan(force=True);
    
  def _rescan (self,force=False):
    # if pounce is on, tell the Purrer to rescan directories
    if self._pounce or force:
      dps = self.purrer.rescan();
      if dps:
        filenames = [dp.filename for dp in dps];
        dprint(2,"new data products:",filenames);
        self.message("Pounced on "+", ".join(filenames));
        if self.new_entry_dialog.addDataProducts(dps) and (force or self._autopounce == self.PounceShow):
          dprint(2,"showing dialog");
          self.new_entry_dialog.show();
    # else read stuff from pipe
    if self.purrpipe:
      do_show = False;
      for command,show,content in self.purrpipe.read():
        if command == "title":
          self.new_entry_dialog.suggestTitle(content);
        elif command == "comment":
          self.new_entry_dialog.addComment(content);
        elif command == "pounce":
          self.new_entry_dialog.addDataProducts(self.purrer.makeDataProducts(
                                                [(content,not show)],unbanish=True));
        else:
          print "Unknown command received from Purr pipe: ",command;
          continue;
        do_show = do_show or show;
      if do_show:
        self.new_entry_dialog.show();
        
  def _addDPFiles (self,*files):
    """callback to add DPs corresponding to files.""";
    # quiet flag is always true
    self.new_entry_dialog.addDataProducts(self.purrer.makeDataProducts(
                          [(file,True) for file in files],unbanish=True));
    
  def _addDPFilesToOldEntry (self,*files):
    """callback to add DPs corresponding to files.""";
    # quiet flag is always true
    self.view_entry_dialog.addDataProducts(self.purrer.makeDataProducts(
                          [(file,True) for file in files],unbanish=True));
    
  def _entrySelectionChanged (self):
    nsel = 0;
    item = self.elv.firstChild();
    selected = [];
    while item:
      if self.elv.isSelected(item) and item._ientry is not None:
        selected.append(item);
      item = item.nextSibling();
    self.weditbtn.setEnabled(len(selected) == 1);
    self.wdelbtn.setEnabled(bool(selected));
      
  def _viewEntryItem (self,item=None,*dum):
    """Pops up the viewer dialog for the entry associated with the given item.
    If 'item' is None, looks for a selected item in the listview.
    The dum arguments are for connecting this to QListView signals such as doubleClicked().
    """;
    # if item not set, look for selected items in listview. Only 1 must be selected.
    select = True;
    if item is None:
      item = self.elv.firstChild();
      selected = [];
      while item:
        if self.elv.isSelected(item) and item._ientry is not None:
          selected.append(item);
        item = item.nextSibling();
      if len(selected) != 1:
        return;
      item = selected[0];
      select = False; # already selected
    else:
      # make sure item is open -- the click will cause it to close
      item.setOpen(True);
    # show dialog
    ientry = getattr(item,'_ientry',None);
    if ientry is not None:
      self._viewEntryNumber(ientry,select=select);
      
  def _viewEntryNumber (self,ientry,select=True):
    """views entry #ientry. Also selects entry in listview if select=True""";
    # pass entry to viewer dialog
    self._viewing_ientry = ientry;
    entry = self.purrer.entries[ientry];
    self.view_entry_dialog.viewEntry(entry,has_prev=(ientry>0),has_next=(ientry<len(self.purrer.entries)-1));
    self.view_entry_dialog.show();
    # select entry in listview
    if select:
      self.elv.clearSelection();
      item = self.elv.firstChild();
      for i in range(ientry):
        item = item and item.nextSibling();
      self.elv.setSelected(item,True);
     
  def _viewPrevEntry (self):
    if self._viewing_ientry is not None and self._viewing_ientry > 0:
      self._viewEntryNumber(self._viewing_ientry-1);
    
  def _viewNextEntry (self):
    if self._viewing_ientry is not None and self._viewing_ientry < len(self.purrer.entries)-1:
      self._viewEntryNumber(self._viewing_ientry+1);
      
  def _showItemContextMenu (self,item,point,col):
    """Callback for contextMenuRequested() signal. Pops up item menu, if defined""";
    menu = getattr(item,'_menu',None);
    if menu: 
      # self._current_item tells callbacks what item the menu was referring to
      self._current_item = item;
      self.elv.clearSelection();
      self.elv.setSelected(item,True);
      menu.exec_loop(point);
    else:
      self._current_item = None;
      
  def _copyItemToClipboard (self):
    """Callback for item menu.""";
    if self._current_item is None:
      return;
    dp = getattr(self._current_item,'_dp',None);
    if dp and dp.archived:
      QApplication.clipboard().setText(dp.fullpath,QClipboard.Clipboard);
      QApplication.clipboard().setText(dp.fullpath,QClipboard.Selection);
      
  def _restoreItemFromArchive (self):
    """Callback for item menu.""";
    if self._current_item is None:
      return;
    dp = getattr(self._current_item,'_dp',None);
    if dp and dp.archived:
      dp.restore_from_archive(parent=self);
  
  def _deleteSelectedEntries (self):
    remaining_entries = [];
    del_entries = [];
    item = self.elv.firstChild();
    hide_viewer = False;
    while item:
      if self.elv.isSelected(item):
        del_entries.append(item._ientry);
        if self._viewing_ientry == item._ientry:
          hide_viewer = True;
      else:
        remaining_entries.append(item._ientry);
      item = item.nextSibling();
    if not del_entries:
      return;
    del_entries = [ self.purrer.entries[i] for i in del_entries ];
    remaining_entries = [ self.purrer.entries[i] for i in remaining_entries ];
    # ask for confirmation
    if len(del_entries) == 1:
      msg = """<P><NOBR>Permanently delete the log entry</NOBR> "%s"?</P>"""%del_entries[0].title;
      if del_entries[0].dps:
        msg += """<P>%d data product(s) saved with this 
                  entry will be deleted as well.</P>"""%len(del_entries[0].dps);
    else:
      msg = """<P>Permanently delete the %d selected log entries?</P>"""%len(del_entries);
      ndp = 0;
      for entry in del_entries:
        ndp += len(filter(lambda dp:not dp.ignored,entry.dps));
      if ndp:
        msg += """<P>%d data product(s) saved with these entries will be deleted as well.</P>"""%ndp;
    if QMessageBox.warning(self,"Deleting log entries",msg,
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    if hide_viewer:
      self.view_entry_dialog.hide();
    # reset entries in purrer and in our log window
    self._setEntries(remaining_entries);
    self.purrer.setLogEntries(remaining_entries);
    # log will have changed, so update the viewer
    self._updateViewer();
    # delete entry files
    for entry in del_entries:
      entry.remove_directory();
      
  def _addEntryItem (self,entry,number,after):
    item = QListViewItem(self.elv,after);
    item.setText(0,self._make_time_label(entry.timestamp));
    item.setText(1," "+(entry.title or ""));
    comment = " "+(entry.comment or "");
    item.setText(2,comment);
    item._ientry = number;
    item._dp = None;
    # now make subitems for DPs
    subitem = None;
    for dp in entry.dps:
      if not dp.ignored:
        subitem = self._addDPSubItem(dp,item,subitem);
    item.setOpen(False);
    return item;
    
  def _addDPSubItem (self,dp,parent,after):
    item = QListViewItem(parent,after);
    item.setText(1,dp.filename);
    item.setText(2,dp.comment or "");
    item._ientry = None;
    item._dp = dp;
    item._menu = self._archived_dp_menu;

  def _make_time_label (self,timestamp):
    return time.strftime("%b %d %H:%M",time.localtime(timestamp));
    
  def _newLogEntry (self,entry):
    """This is called when a new log entry is created""";
    # add entry to purrer
    self.purrer.addLogEntry(entry);
    # add entry to listview if it is not an ignored entry
    # (ignored entries only carry information about DPs to be ignored)
    if not entry.ignore:
      lastitem = self.elv.lastItem();
      while lastitem and isinstance(lastitem.parent(),QListViewItem):
        lastitem = lastitem.parent();
      self._addEntryItem(entry,len(self.purrer.entries)-1,lastitem);
    # log will have changed, so update the viewer
    if not entry.ignore:
      self._updateViewer();
      self.show();
    
  def _entryChanged (self,entry):
    """This is called when a log entry is changed""";
    # resave the log
    self.purrer.save();
    # log will have changed, so update the viewer
    self._updateViewer();
    
  def _regenerateLog (self):
    if QMessageBox.question(self.viewer_dialog,"Regenerate log","""<P><NOBR>Do you really want to regenerate the
      entire</NOBR> log? This can be a time-consuming operation.</P>""",
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    self.purrer.save(refresh=True);
    self._updateViewer();
  