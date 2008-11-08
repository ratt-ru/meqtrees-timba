_tdl_no_reimport = True;

import os.path
import time

from qt import *

import Purr
import Purr.Editors
import Purr.Pipe
from Purr import Config,pixmaps,dprint,dprintf


class BusyIndicator (object):
  def __init__ (self):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
  def __del__ (self):
    QApplication.restoreOverrideCursor();

class MainWindow (QMainWindow):
  def __init__ (self,parent,hide_on_close=False):
    QMainWindow.__init__(self,parent);
    self._hide_on_close = hide_on_close;
    # replace the BusyIndicator class with a GUI-aware one
    Purr.BusyIndicator = BusyIndicator;
    # autopounce is on if GUI checkbox is on
    # pounce is on if autopounce is on, or the new Entry dialog is visible.
    self._autopounce = self._pounce = False;
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
    self.wpounce = QCheckBox("pounce on new/updated files",cw);
    self.wpounce.setChecked(self._autopounce);
    self.connect(self.wpounce,SIGNAL("toggled(bool)"),self.enablePounce);
    toplo.addWidget(self.wpounce,1);
    about_btn = QPushButton("About...",cw);
    about_btn.setMinimumWidth(128);
    about_btn.setFlat(True);
    about_btn.setIconSet(pixmaps.purr_logo.iconset());
    toplo.addWidget(about_btn);
    self._about_dialog = QMessageBox("About PURR","""
        <P>PURR ("<B>P</B>URR is <B>U</B>seful for <B>R</B>emembering <B>R</B>eductions", or
        "<B>P</B>URR <B>U</B>sually <B>R</B>emembers <B>R</B>eductions", for those working with the
        development version) is a tool for
        automatically keeping a log of your data reduction operations. PURR will watch your working directories
        for new files (called "data products"), and upon seeing any, it will "pounce" -- that is, offer
        you the option of saving them to a log, along with descriptive comments. It will then
        generate an HTML page with a rendering of your log and data products.</P>
        <P>PURR is not watching any directories right now. Click on the "pounce" option to start
        watching your current directory.</P>""",
        QMessageBox.NoIcon,
        QMessageBox.Ok,QMessageBox.NoButton,QMessageBox.NoButton,cw);
    self._about_dialog.setIconPixmap(pixmaps.purr_logo.pm()); 
    self.connect(about_btn,SIGNAL("clicked()"),self._about_dialog.exec_loop);
    cwlo.addSpacing(5);
    self.dir_label = QLabel("Directory: none",cw);
    cwlo.addWidget(self.dir_label);
    title_lo = QHBoxLayout(cwlo);
    self.title_label = QLabel("Log title: none",cw);
    title_lo.addWidget(self.title_label,1);
    self.wrename = QPushButton("Rename...",cw);
    self.wrename.setMinimumWidth(128);
    self.wrename.setFlat(True);
    self.wrename.setEnabled(False);
    self.connect(self.wrename,SIGNAL("clicked()"),self._renameLogDialog);
    title_lo.addWidget(self.wrename,0);
    cwlo.addSpacing(5);
    # listview of log entries
    self.elv = QListView(cw);
    cwlo.addWidget(self.elv);
    self.elv.addColumn("date/time");
    self.elv.addColumn("title",128);
    self.elv.addColumn("comment",128);
    self.elv.header().hide();
    self.elv.setAllColumnsShowFocus(True);
    self.elv.setShowToolTips(True);
    self.elv.setSorting(-1);
    self.elv.setResizeMode(QListView.LastColumn);
    self.elv.setColumnAlignment(2,Qt.AlignLeft|Qt.AlignTop);
    self.elv.setSelectionMode(QListView.Extended);
    self.connect(self.elv,SIGNAL("selectionChanged()"),self._entrySelectionChanged);
    # buttons at bottom
    cwlo.addSpacing(5);
    btnlo = QHBoxLayout(cwlo);
    self.wnewbtn = QPushButton("New...",cw);
    self.wnewbtn.setFlat(True);
    self.wnewbtn.setEnabled(False);
    btnlo.addWidget(self.wnewbtn);
    btnlo.addSpacing(5);
    self.weditbtn = QPushButton("Edit...",cw);
    self.weditbtn.setFlat(True);
    self.weditbtn.setEnabled(False);
    btnlo.addWidget(self.weditbtn);
    btnlo.addSpacing(5);
    self.wdelbtn = QPushButton("Delete",cw);
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
      return QMainWindow.closeEvent(self,ev);
    
  def message (self,msg,ms=2000,sub=False):
    if sub:
      if self._prev_msg:
        msg = ": ".join((self._prev_msg,msg));
    else:
      self._prev_msg = msg;
    self.statusBar().message(msg,ms);
    QApplication.eventLoop().processEvents(QEventLoop.ExcludeUserInput);
    
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
        purrer.watchDirectories(watchdirs);
        break;
    # no purrer found, make a new one
    else:
      dprint(1,"creating new Purrer object");
      purrer = Purr.Purrer(dirname,watchdirs);
      self.purrer_stack.insert(0,purrer);
      # discard end of stack
      self.purrer_stack = self.purrer_stack[:3];
    # have we changed the current purrer? Update our state then
    self.message("Attached to directory %s"%purrer.dirname);
    # reopen pipe
    self.purrpipe = Purr.Pipe.open(purrer.dirname);
    if purrer is not self.purrer:
      dprint(1,"current Purrer changed, updating state");
      self.purrer = purrer;
      self.new_entry_dialog.hide();
      self.new_entry_dialog.reset();
      self.new_entry_dialog.setDefaultDirs(*purrer.watched_dirs);
      self._setEntries(self.purrer.getLogEntries());
      self._updateNames();
      # set autopounce property from purrer. Reset _pounce to false -- this will cause
      # checkPounceStatus() into a rescan if autopounce is on.
      self.enablePounce(purrer.autopounce);
      self._pounce = False;
      self._checkPounceStatus();
    
  def setLogTitle (self,title):
    self.purrer.setLogTitle(title);
    self._updateNames();
    
  def enablePounce (self,enable=True):
    if enable and not self.purrer:
      self.attachDirectory('.');
    self._autopounce = enable;
    if self.purrer:
      self.purrer.autopounce = enable;
    self.wpounce.setChecked(enable);
    self._checkPounceStatus();
    
  def _updateNames (self):
    self.wnewbtn.setEnabled(True);
    self.wrename.setEnabled(True);
    self._about_dialog.setText("""
    <P>PURR ("<B>P</B>URR is <B>U</B>seful for <B>R</B>emembering <B>R</B>eductions", or
    "<B>P</B>URR <B>U</B>sually <B>R</B>emembers <B>R</B>eductions", for those working with the
    development version) is a tool for
    automatically keeping a log of your data reduction operations. PURR will watch your working directories
    (<tt>%s</tt>) for new files (called "data products"), and upon seeing any, it will "pounce" -- that is, offer
    you the option of saving them to a log, along with descriptive comments. It will then
    generate an HTML page with a rendering of your log and data products.</P>
    
    <P>Your current log resides in <tt>%s</tt>. Point your browser to <tt>index.html</tt> therein.</P>
    """%(", ".join(self.purrer.watched_dirs),self.purrer.logdir));
    self.dir_label.setText("Directory: %s"%self.purrer.dirname);
    self.title_label.setText("Log title: <B>%s</B>"%(self.purrer.logtitle or "Unnamed log"));
    
  def _setEntries (self,entries):
    self.elv.clear();
    item = None;
    for entry in entries:
      item = self._addEntryItem(entry,item);
      
  def _renameLogDialog (self):
    (title,ok) = QInputDialog.getText("PURR: Rename Log",
                  "Enter new name for this log",QLineEdit.Normal,self.purrer.logtitle,self);
    if ok and title != self.purrer.logtitle:
      self.setLogTitle(title);
      
  def _checkPounceStatus (self):
    pounce = self._autopounce or self.new_entry_dialog.isVisible();
    # rescan, if going from not-pounce to pounce
    if pounce and not self._pounce:
      self._rescan();
    self._pounce = pounce;
    # start timer -- we need it running to check the purr pipe, anyway
    self._timer.start(2000);
      
  def _rescan (self):
    # if pounce is on, tell the Purrer to rescan directories
    if self._pounce:
      dps = self.purrer.rescan();
      if dps:
        filenames = [dp.filename for dp in dps];
        dprint(2,"new data products:",filenames);
        self.message("pounced on "+", ".join(filenames));
        if self.new_entry_dialog.addDataProducts(dps):
          dprint(2,"showing dialog");
          self.new_entry_dialog.show();
    # else read stuff from pipe
    do_show = False;
    for line in self.purrpipe.read():
      command,show,content = line.split(":",2);
      if command == "title":
        self.new_entry_dialog.suggestTitle(content);
      elif command == "comment":
        self.new_entry_dialog.addComment(content);
      elif command == "pounce":
        self.new_entry_dialog.addDataProducts(self.purrer.makeDataProducts((content,not show)));
      else:
        print "Unknown command received from Purr pipe: ",line;
        continue;
      do_show = do_show or int(show);
    if do_show:
      self.new_entry_dialog.show();
        
        
  def _addDPFiles (self,*files):
    """callback to add DPs corresponding to files.""";
    # quiet flag is always true
    self.new_entry_dialog.addDataProducts(self.purrer.makeDataProducts(*[(file,True) for file in files]));
    
  def _entrySelectionChanged (self):
    nsel = 0;
    item = self.elv.firstChild();
    while item:
      if self.elv.isSelected(item):
        nsel += 1;
      item = item.nextSibling();
    self.weditbtn.setEnabled(nsel == 1);
    self.wdelbtn.setEnabled(nsel);
    
  def _deleteSelectedEntries (self):
    remaining_entries = [];
    del_entries = [];
    item = self.elv.firstChild();
    while item:
      if self.elv.isSelected(item):
        del_entries.append(item._entry);
      else:
        remaining_entries.append(item._entry);
      item = item.nextSibling();
    if not del_entries:
      return;
    # ask for confirmation
    if len(del_entries) == 1:
      msg = """<P>Permanently delete the log entry "%s"?</P>"""%del_entries[0].title;
      if del_entries[0].dps:
        msg += """<P>%d data product(s) saved with this 
                  entry will be deleted as well.</P>"""%len(del_entries[0].dps);
    else:
      msg = """<P>Permanently delete the %d selected log entries?</P>"""%len(del_entries);
      ndp = 0;
      for entry in del_entries:
        ndp += len(entry.dps);
      if ndp:
        msg += """<P>%d data product(s) saved with these entries will be deleted as well.</P>"""%ndp;
    if QMessageBox.question(self,"Deleting log entries",msg,
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    # reset entries in purrer and in our log window
    self._setEntries(remaining_entries);
    self.purrer.setLogEntries(remaining_entries);
    # delete entry files
    for entry in del_entries:
      entry.remove_directory();
      
  def _addEntryItem (self,entry,after):
    item = QListViewItem(self.elv,after);
    item.setText(0,self._make_time_label(entry.timestamp));
    item.setText(1," "+entry.title);
    item.setText(2," "+entry.comment);
    item._entry = entry;
    return item;

  def _make_time_label (self,timestamp):
    return time.strftime("%b %d %H:%M",time.localtime(timestamp));
    
  def _newLogEntry (self,entry):
    """This is called when a new log entry is created""";
    self._addEntryItem(entry,self.elv.lastItem());
    self.purrer.addLogEntry(entry);
    self.show();
    