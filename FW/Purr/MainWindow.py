import os.path
import time

from qt import *

import Purr.Editors
from Purr import Config,dprint,dprintf
from Purr import PurrLogo

class MainWindow (QMainWindow):
  def __init__ (self,parent,purrer):
    QMainWindow.__init__(self,parent);
    self.purrer = purrer;
    self.setCaption("PURR");
    self.setIcon(PurrLogo.purr_logo.pm());
    cw = QWidget(self);
    self.setCentralWidget(cw);
    cwlo = QVBoxLayout(cw);
    cwlo.setMargin(5);
    # logo.setPixmap(PurrLogo.purr_logo.pm());
    # toplo.addWidget(logo);
    about_btn = QPushButton("About PURR...",cw);
    about_btn.setFlat(True);
    about_btn.setIconSet(PurrLogo.purr_logo.iconset());
    cwlo.addWidget(about_btn);
    self._about_dialog = QMessageBox("About PURR","",QMessageBox.NoIcon,
                        QMessageBox.Ok,QMessageBox.NoButton,QMessageBox.NoButton,cw);
    self._about_dialog.setIconPixmap(PurrLogo.purr_logo.pm()); 
    self.connect(about_btn,SIGNAL("clicked()"),self._about_dialog.exec_loop);
    cwlo.addSpacing(5);
    self.wwatchbtn = QCheckBox("pounce on new/updated files",cw);
    self.wwatchbtn.setChecked(True);
    self.connect(self.wwatchbtn,SIGNAL("toggled(bool)"),self._updateWatchStatus);
    cwlo.addWidget(self.wwatchbtn);
    cwlo.addSpacing(5);
    title_lo = QHBoxLayout(cwlo);
    self.title_label = QLabel("Log title: <b>Unnamed</b>",cw);
    title_lo.addWidget(self.title_label,1);
    change_btn = QPushButton("Rename...",cw);
    change_btn.setFlat(True);
    self.connect(change_btn,SIGNAL("clicked()"),self._renameLogDialog);
    title_lo.addWidget(change_btn,0);
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
    newbtn = QPushButton("New...",cw);
    newbtn.setFlat(True);
    btnlo.addWidget(newbtn);
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
    # editor dialog for new entry
    self.new_entry_dialog = Purr.Editors.NewLogEntryDialog(self);
    self.connect(self.new_entry_dialog,PYSIGNAL("newLogEntry()"),self._newLogEntry);
    self.connect(newbtn,SIGNAL("clicked()"),self.new_entry_dialog.show);
    self.connect(self.new_entry_dialog,PYSIGNAL("shown()"),self._updateWatchStatus);
    # resize selves
    width = Config.getint('main-window-width',512);
    height = Config.getint('main-window-height',512);
    self.resize(QSize(width,height));
    
  def resizeEvent (self,ev):
    QMainWindow.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('main-window-width',sz.width());
    Config.set('main-window-height',sz.height());
    
  def setLogTitle (self,title):
    self.logtitle = title or "Unnamed";
    self.title_label.setText("Log title: <B>%s</B>"%self.logtitle);
    
  def setDirName (self,dirname,logdir):
    self.dirname = os.path.abspath(dirname);
    self.logdir = os.path.abspath(logdir);
    self._about_dialog.setText("""
    <P>PURR (<B>P</B>URR is <B>U</B>seful for <B>R</B>emembering <B>R</B>eductions) is a tool for
    automatically keeping a log of your data reduction operations. PURR will watch your working directories (currently <tt>%s</tt>) for new files (called "data products"), and will offer you the option
    of saving them to a calibration log, along with descriptive comments.
    
    <P>Your current log resides in <tt>%s</tt>. Point your browser to <tt>index.html</tt> therein.</P>
    """%(self.dirname,self.logdir));
    
  def setEntries (self,entries):
    self.elv.clear();
    item = None;
    for entry in entries:
      item = self._addEntryItem(entry,item);
      
  def _renameLogDialog (self):
    (title,ok) = QInputDialog.getText("PURR: Rename Log",
                  "Enter new name for this log",QLineEdit.Normal,self.logtitle,self);
    if ok:
      self.purrer.setTitle(title);
      
  def _updateWatchStatus (self,*dum):
    watching = self.wwatchbtn.isChecked() or self.new_entry_dialog.isVisible();
    self.purrer.enableWatching(watching);
    
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
    # reset entries in purrer, this will cause our setEntires() to be called
    self.purrer.setEntries(remaining_entries);
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

  def newDataProducts (self,dps):
    if not dps:
      return;
    dprint(2,"new data products:",[dp.filename for dp in dps]);
    if self.new_entry_dialog.addDataProducts(dps):
      dprint(2,"showing dialog");
      self.new_entry_dialog.show();
      
  def _make_time_label (self,timestamp):
    return time.strftime("%b %d %H:%M",time.localtime(timestamp));
    
  def _newLogEntry (self,entry):
    """This is called when a new log entry is created""";
    self._addEntryItem(entry,self.elv.lastItem());
    self.purrer.newLogEntry(entry);
    