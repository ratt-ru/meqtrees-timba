
from qt import *
import time
import os
import os.path
import sets

from Purr import Config
from Purr import PurrLogo
import Purr.LogEntry

class LogEntryEditor (QWidget):
  """This is a base class providing a widget for log entry editing.
  It is specialized by NowLogEntryEditor and ExistingLogEntryEditor
  """;
  def __init__ (self,parent):
    QWidget.__init__(self,parent);
    lo_top = QVBoxLayout(self);
    lo_top.setMargin(5);
    # create comment editor
    # create title and timestamp label, hide timestamp until it is set (below)
    lo_topline = QHBoxLayout(lo_top);
    self.wtoplabel = QLabel("New entry title:",self);
    self.wtimestamp = QLabel("",self);
    lo_topline.addWidget(self.wtoplabel);
    lo_topline.addStretch(1);
    lo_topline.addWidget(self.wtimestamp);
    # add title editor
    self.wtitle   = QLineEdit(self);
    lo_top.addWidget(self.wtitle);
    # add comment editor
    lo_top.addSpacing(5);
    lo_top.addWidget(QLabel("Comment:",self));
    self.wcomment = QTextEdit(self);
    lo_top.addWidget(self.wcomment);
    # generate frame for the "Data products" listview
    lo_top.addSpacing(5);
    lo_top.addWidget(QLabel("""<P>Data products are listed below. Click on the "action" column to select
          what to do with a product. Click on the "rename" column to rename the product.
          Click "comment" to enter a comment.</P>""",self));
    # create DP listview
    ndplv = self.wdplv = QListView(self);
    lo_top.addWidget(self.wdplv);
    ndplv.addColumn("action");
    ndplv.setColumnAlignment(0,Qt.AlignHCenter);
    ndplv.addColumn("filename");
    ndplv.addColumn("rename");
    ndplv.addColumn("comment");
    ndplv.setSorting(-1);
    ndplv.setResizeMode(QListView.LastColumn);
    ndplv.setAllColumnsShowFocus(True);
    ndplv.header().show();
    ndplv.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    self.connect(ndplv,SIGNAL("clicked(QListViewItem*,const QPoint &,int)"),self._lv_item_clicked);
    # other internal init
    self.reset();
    
  # The keys of this dict are valid DataProduct policies.
  # The values are the "next" polciy when cycling through
  _policies = dict(copy="move",move="ignore",ignore="copy");
    
  def reset (self):
    self.entry = self._timestamp = None;
    self.wtimestamp.hide();
    self.setEntryTitle("Untitled entry");
    self.setEntryComment("No comment");
    self.wdplv.clear();
    self.dpitems = {};
    
  def _lv_item_clicked (self,item,point,column):
    if not item:
      return;
    if column == 0:
      item._policy = self._policies[item._policy];
      item.setText(0,item._policy);
    elif column in [2,3]:
      item.startRename(column);
    
  def updateEntry (self,timestamp=None):
    """Updates entry object with current content of dialog. Creates new LogEntry if needed.
    """;
    # form up new entry
    title = str(self.wtitle.text());
    comment = str(self.wcomment.text());
    # process comment string -- eliminate single newlines, make double-newlines separate paragraphs
    comment = "\n".join([ pars.replace("\n"," ") for pars in comment.split("\n\n") ]);
    dps = [];
    item = self.wdplv.firstChild();
    while item:
      dps.append(Purr.DataProduct(item._filename,policy=item._policy,
                               rename=str(item.text(2)),comment=str(item.text(3))));
      item = item.nextSibling();
    if self.entry:
      self.entry.update(title,comment,dps,timestamp=timestamp);
    else:
      self._timestamp = timestamp or time.time();
      self.entry = Purr.LogEntry(self._timestamp,title,comment,dps)
    return self.entry;
    
  def setEntry (self,entry):
    """Populates the dialog with contents of an existing entry.""";
    self.entry = entry;
    self.setEntryTitle(entry.title);
    self.setEntryComment(entry.comment);
    self.wdplv.clear();
    item = None;
    # non-ignored items first
    for dp in [ dp for dp in entry.dps if dp.policy != 'ignore' ]:
      item = self._makeDPItem(dp,item);
    # ignored items go last
    for dp in [ dp for dp in entry.dps if dp.policy == 'ignore' ]:
      item = self._makeDPItem(dp,item);
    self.setTimestamp(entry.timestamp);
    self.showColumn(0,False);
  
  def _makeDPItem (self,dp,after):
    item = QListViewItem(self.wdplv,after);
    item._filename = dp.filename;
    item._policy = dp.policy;
    item.setText(0,dp.policy);
    item.setText(1,os.path.basename(dp.filename));
    item.setText(2,os.path.basename(dp.rename or filename));
    item.setRenameEnabled(2,True);
    item.setRenameEnabled(3,True);
    self.dpitems[dp.filename] = item;
    return item;
  
  def addDataProducts(self,dps):
    # this flag will be set if any new files are added, or if existing
    # files (that have been checked on) are updated
    updated = False;
    for dp in dps:
      item = self.dpitems.get(dp.filename);
      if not item:
        # ignore DPs added to end, non-ingored added to head
        if dp.policy == "ignore":
          after = self.wdplv.lastItem();
        else:
          after = None;
        item = self._makeDPItem(dp,after);
      updated = updated or item._policy != "ignore";
    return updated;
      
  def entryTitle (self):
    return self.wtitle.text();
  
  def setEntryTitle (self,title,select=True):
    self.wtitle.setText(title);
    if select:
      self.wtitle.selectAll();
      
  def setEntryComment (self,comment,select=True):
    self.wcomment.setText(comment);
    if select:
      self.wcomment.selectAll();
    
  def setTimestamp (self,timestamp):
    print timestamp;
    self._timestamp = timestamp;
    txt = time.strftime("%x %X",time.localtime(timestamp));
    self.wtimestamp.setText(txt);
    self.wtimestamp.show();
      

class NewLogEntryDialog (QDialog):
  class DialogTip (QToolTip):
    def __init__ (self,parent):
      QToolTip.__init__(self,parent);
      self.parent = parent;
    def maybeTip (self,pos):
      print "maybetip",pos;
      parent = self.parent;
      if parent._has_tip:
        rect = QRect(pos.x()-20,pos.y()-20,40,40);
        self.tip(rect,parent._has_tip);
        parent._has_tip = None;
  
  def __init__ (self,parent,*args):
    QDialog.__init__(self,parent,*args);
    self.setCaption("PURR: New Log Entry");
    self.setIcon(PurrLogo.purr_logo.pm());
    self.setModal(False);
    # create pop-up tip
    self._has_tip = None;
    self._dialog_tip = self.DialogTip(self);
    # create editor
    lo = QVBoxLayout(self);
    self.editor = LogEntryEditor(self);
    lo.addWidget(self.editor);
    lo.addSpacing(5);
    # create button bar
    btnfr = QFrame(self);
    btnfr.setMargin(5);
    lo.addWidget(btnfr);
    lo.addSpacing(5);
    btnfr_lo = QHBoxLayout(btnfr);
    newbtn = QPushButton("Add new entry",btnfr);
    cancelbtn = QPushButton("Cancel",btnfr);
    QObject.connect(newbtn,SIGNAL("clicked()"),self.addNewEntry);
    QObject.connect(cancelbtn,SIGNAL("clicked()"),self.hide);
    btnfr_lo.setMargin(5);
    btnfr_lo.addWidget(newbtn,1);
    btnfr_lo.addStretch(1);
    btnfr_lo.addWidget(cancelbtn,1);
    self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    # resize selves
    width = Config.getint('entry-editor-width',256);
    height = Config.getint('entry-editor-height',256);
    self.resize(QSize(width,height));
    
  def resizeEvent (self,ev):
    QDialog.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('entry-editor-width',sz.width());
    Config.set('entry-editor-height',sz.height());
  
  def showEvent (self,ev):
    QDialog.showEvent(self,ev);
    self.emit(PYSIGNAL("shown()"),(True,));
    
  def hideEvent (self,ev):
    QDialog.hideEvent(self,ev);
    self.emit(PYSIGNAL("shown()"),(False,));

  def reset (self):
    self.editor.reset();
    
  def addDataProducts (self,dps):
    updated = self.editor.addDataProducts(dps);
    if updated:
      self._has_tip = """<P>This dialog popped up because new data products
        have been detected and pounced on. If you dislike this behaviour, disable the
        "pounce" option in the main PURR window.<P>""";
    return updated;
    
  def addNewEntry (self):
    # confirm with user
    if QMessageBox.question(self,"Adding new entry","""<P>Do you really want to add
          a new log entry titled "%s"?"""%(self.editor.entryTitle()),
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    # add entry
    entry = self.editor.updateEntry();
    self.emit(PYSIGNAL("newLogEntry()"),(entry,));
    self.editor.reset();
    self.hide();
    
class ExistingLogEntryEditor (LogEntryEditor):
  def __init__ (self,parent,*args):
    QDialog.__init__(self,parent,*args);
    self.setModal(False);
    lo = QVBoxLayout(self);
    # create editor
    self.editor = LogEntryEditor(self);
    lo.addWidget(self.editor);
    # create button bar
    btnfr = QFrame(self);
    lo.addWidget(btnfr);
    btnfr_lo = QHBoxLayout(btnfr);
    savebtn = QPushButton("Save",btnfr);
    QObject.connect(savebtn,SIGNAL("clicked()"),self.saveEntry);
    cancelbtn = QPushButton("Cancel",btnfr);
    QObject.connect(cancelbtn,SIGNAL("clicked()"),self.cancelEntry);
    btnfr_lo.addWidget(savebtn,1);
    btnfr_lo.addStretch(1);
    btnfr_lo.addWidget(cancelbtn,1);
    # resize selves
    width = Config.getint('entry-editor-width',256);
    height = Config.getint('entry-editor-height',256);
    self.resize(QSize(width,height));
    
  def resizeEvent (self,ev):
    QDialog.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('entry-editor-width',sz.width());
    Config.set('entry-editor-height',sz.height());

  def saveEntry (self):
    if QMessageBox.question(self,"Saving existing entry","""<P>Do you really want to save changes to this
          log entry?""",
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    self.editor.updateEntry();
    self.editor.entry.save();
    
  def cancelEntry (self):
    self.hide();
    self.emit(PYSIGNAL("cancelEntry()"),());
    
