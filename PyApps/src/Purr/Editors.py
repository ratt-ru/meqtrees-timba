_tdl_no_reimport = True;

from qt import *
import time
import os
import os.path
import sets

from Purr import Config,pixmaps
import Purr.LogEntry
import Purr.Render

class LogEntryEditor (QWidget):
  """This is a base class providing a widget for log entry editing.
  It is specialized by NowLogEntryEditor and ExistingLogEntryEditor
  """;
  def __init__ (self,parent):
    QWidget.__init__(self,parent);
    lo_top = QVBoxLayout(self);
    lo_top.setResizeMode(QLayout.Minimum);
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
    self.connect(self.wtitle,SIGNAL("textChanged(const QString&)"),self._titleChanged);
    # add comment editor
    lo_top.addSpacing(5);
    lo_top.addWidget(QLabel("Comment:",self));
    self.wcomment = QTextEdit(self);
    self.wcomment.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self.connect(self.wcomment,SIGNAL("textChanged()"),self._commentChanged);
    lo_top.addWidget(self.wcomment);
    # generate frame for the "Data products" listview
    lo_top.addSpacing(5);
    dpline = QWidget(self);
    lo_top.addWidget(dpline);
    dpline.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    lo_dpline = QHBoxLayout(dpline);
    dp_tip_text = """<P>"Data products" are files that will be archived along with this log entry. If "pounce" 
      is enabled, PURR will watch your directories for new or updated files, and insert them in this list
      automatically. You can also click on "Add..." to add files manually.</P>
      
      <P>Click on the "action" column to select what to do with a file. Click on the "rename" column 
      to archive the file under a different name. Click "comment" to enter a comment for the file.</P>""";
    label = QLabel("Data products:",dpline)
    QToolTip.add(label,dp_tip_text);
    lo_dpline.addWidget(label);
    lo_dpline.addStretch(1);
    self.wnewdp = QPushButton(pixmaps.folder_open.iconset(),"Add...",dpline);
    self.connect(self.wnewdp,SIGNAL("clicked()"),self._showAddDialog);
    self._add_dp_dialog = None;
    lo_dpline.addWidget(self.wnewdp);
    # create DP listview
    ndplv = self.wdplv = QListView(self);
    ndplv.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    lo_top.addWidget(self.wdplv);
    # insert columns, and numbers for them
    self.ColAction   = ndplv.columns(); ndplv.addColumn("action");
    self.ColFilename = ndplv.columns(); ndplv.addColumn("filename",120);
    self.ColRename   = ndplv.columns(); ndplv.addColumn("rename",120);
    self.ColRender   = ndplv.columns(); ndplv.addColumn("render");
    self.ColComment  = ndplv.columns(); ndplv.addColumn("comment");
    ndplv.setColumnAlignment(self.ColAction,Qt.AlignHCenter);
    ndplv.setColumnAlignment(self.ColFilename,Qt.AlignRight);
    ndplv.setColumnAlignment(self.ColRename,Qt.AlignRight);
    ndplv.setColumnAlignment(self.ColRender,Qt.AlignHCenter);
    ndplv.setColumnAlignment(self.ColComment,Qt.AlignLeft);
    ndplv.setSorting(-1);
    # sort out resizing modes
    ndplv.header().setMovingEnabled(False);
    ndplv.header().setResizeEnabled(False,self.ColAction);
    ndplv.header().setResizeEnabled(False,self.ColRender);
    ndplv.setResizeMode(QListView.LastColumn);
    # setup other properties of the listview
    ndplv.setAllColumnsShowFocus(True);
    ndplv.setShowToolTips(True); 
    ndplv.setDefaultRenameAction(QListView.Accept); 
    ndplv.setSelectionMode(QListView.NoSelection);
    ndplv.header().show();
    ndplv.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    self.connect(ndplv,SIGNAL("clicked(QListViewItem*,const QPoint &,int)"),self._lv_item_clicked);
    # other internal init
    self.reset();
    
  # The keys of this dict are valid DataProduct policies.
  # The values are the "next" polciy when cycling through
  _policy_cycle = dict(copy="move",move="ignore",ignore="copy");
  _policy_icons = dict(copy='copy',move='move',ignore='grey_round_cross');
    
  def hideEvent (self,event):
    QWidget.hideEvent(self,event);
    if self._add_dp_dialog:
      self._add_dp_dialog.hide();
    
  def reset (self):
    self.entry = self._timestamp = None;
    self.wtimestamp.hide();
    self.setEntryTitle("Untitled entry");
    self.setEntryComment("No comment");
    self.wdplv.clear();
    self.dpitems = {};
    self._default_dir = ".";
    self._title_changed = self._comment_changed = False;
    self._last_auto_comment = None;
    
  def setDefaultDirs (self,*dirnames):
    self._default_dirs = dirnames;
    
  class AddDataProductDialog (QFileDialog):
    """This is a file selection dialog with an extra quick-jump combobox for 
    multiple directories""";
    def __init__ (self,parent):
      QFileDialog.__init__(self);
      self.setCaption("PURR: Add Data Products");
      self.setMode(QFileDialog.ExistingFiles);
      self.dirlist = None;
      # make quick-jump combobox
      self.wlabel = QLabel("Quick jump:",self);
      self.wdirlist = QComboBox(False,self);
      self.wdirlist.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
      self.connect(self.wdirlist,SIGNAL("activated(const QString &)"),self.setDir);
      self.addWidgets(self.wlabel,self.wdirlist,None);
      # connect signals (translates into a PYSIGNAL with string arguments)
      self.connect(self,SIGNAL("filesSelected(const QStringList&)"),self._filesSelected);
    
    def setDirList (self,dirlist):
      if dirlist != self.dirlist:
        self.dirlist = dirlist;
        self.wdirlist.clear();
        for dirname in dirlist:
          self.wdirlist.insertItem(dirname);
        self.wlabel.setShown(len(dirlist)>1);
        self.wdirlist.setShown(len(dirlist)>1);
          
    def _filesSelected (self,filelist):
      self.emit(PYSIGNAL("filesSelected()"),tuple(map(str,filelist)))
  
  def _showAddDialog (self):
    if not self._add_dp_dialog:
      self._add_dp_dialog = self.AddDataProductDialog(self);
      self.connect(self._add_dp_dialog,PYSIGNAL("filesSelected()"),
                   self,PYSIGNAL("filesSelected()"));
      # add quick-jump combobox
    self._add_dp_dialog.setDirList(self._default_dirs);
    self._add_dp_dialog.show();
    self._add_dp_dialog.raiseW();
    
  def _lv_item_clicked (self,item,point,column):
    if not item:
      return;
    if column == self.ColAction:
      self._setItemPolicy(item,self._policy_cycle.get(item._policy,"copy"));
    elif column == self.ColRender:
      item._render = (item._render+1)%len(item._renderers);
      item.setText(self.ColRender,item._renderers[item._render]);
    elif column in [self.ColRename,self.ColComment]:
      item.startRename(column);
      
  def _setItemPolicy (self,item,policy):
    pmname = self._policy_icons.get(policy);
    if pmname is None:
      policy = "copy";
      pmname = self._policy_icons.get(policy);
    item._policy = policy;
    item.setText(self.ColAction,policy);
    pixmap = getattr(pixmaps,pmname,None);
    if pixmap:
      item.setPixmap(self.ColAction,pixmap.pm());
    else:
      item.setPixmap(self.ColAction,None);
      
  def _makeDPItem (self,dp,after):
    item = QListViewItem(self.wdplv,after);
    item._sourcepath = dp.sourcepath;
    self._setItemPolicy(item,dp.policy);
    item.setText(self.ColFilename,os.path.basename(dp.sourcepath));
    item.setText(self.ColRename,dp.filename);
    item.setText(self.ColComment,dp.comment or "");
    item.setRenameEnabled(self.ColRename,True);
    item.setRenameEnabled(self.ColComment,True);
    # get list of available renderers
    item._renderers = Purr.Render.getRenderers(dp.fullpath or dp.sourcepath);
    item._render = 0;
    item.setText(self.ColRender,item._renderers[0]);
    # add to map of items
    self.dpitems[item._sourcepath] = item;
    return item;
  
  def _titleChanged (self,*dum):
    self._title_changed = True;
    
  def _commentChanged (self,*dum):
    self._comment_changed = True;
  
  def suggestTitle(self,title):
    """Suggests a title for the entry.
    If title has been manually edited, suggestion is ignored.""";
    if not self._title_changed or not str(self.wtitle.text()):
      self.wtitle.setText(title);
      self._title_changed = False;
    
  def addComment(self,comment):
    # get current comment text
    if self._comment_changed:
      cur_comment = str(self.wcomment.text());
      cpos = self.wcomment.getCursorPosition();
    else:
      cur_comment = "";
      cpos = None;
    # always add newline to new comment
    comment += "\n";
    # no current comments? Replace
    if not cur_comment:
      cur_comment = comment;
    # else was last comment auto-added here? Do not start paragraph
    elif self._last_auto_comment and cur_comment.endswith(self._last_auto_comment):
      cur_comment += comment;
    # else start a new paragraph and add comment
    else:
      cur_comment += "\n"+comment;
    self._last_auto_comment = comment;
    # update widget
    self.wcomment.setText(cur_comment);
    if cpos:
      cpos = self.wcomment.setCursorPosition(*cpos);
    
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
      dps.append(Purr.DataProduct(sourcepath=item._sourcepath,policy=item._policy,
                                  filename=str(item.text(self.ColRename)),
                                  render=str(item.text(self.ColRender)),
                                  comment=str(item.text(self.ColComment))));
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
    self.dpitems = {};
    item = None;
    # non-ignored items first
    for dp in [ dp for dp in entry.dps if dp.policy != 'ignore' ]:
      item = self._makeDPItem(dp,item);
    # ignored items go last
    for dp in [ dp for dp in entry.dps if dp.policy == 'ignore' ]:
      item = self._makeDPItem(dp,item);
    self.setTimestamp(entry.timestamp);
    self.showColumn(0,False);
  
  def addDataProducts(self,dps):
    """Adds data products to dialog.
      dps is a list of (dp,quiet) pairs. The quiet flag indicates that a DP is to be added
      quietly (i.e. no need to show the dialog)
    """;
    # this flag will be set if any new non-quiet dps are added, or if existing
    # non-quiet dps (that have been checked on) are updated
    updated = False;
    for dp in dps:
      item = self.dpitems.get(dp.sourcepath);
      if not item:
        # ignore DPs added to end, non-ingored added to head
        if dp.policy == "ignore":
          after = self.wdplv.lastItem();
        else:
          after = None;
        item = self._makeDPItem(dp,after);
      updated = updated or (not dp.quiet and item._policy != "ignore");
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
      parent = self.parent;
      if parent._has_tip:
        rect = QRect(pos.x()-20,pos.y()-20,40,40);
        self.tip(rect,parent._has_tip);
        parent._has_tip = None;
  
  def __init__ (self,parent,*args):
    QDialog.__init__(self,parent,*args);
    self.setCaption("PURR: New Log Entry");
    self.setIcon(pixmaps.purr_logo.pm());
    self.setModal(False);
    # create pop-up tip
    self._has_tip = None;
    self._dialog_tip = self.DialogTip(self);
    # create editor
    lo = QVBoxLayout(self);
    lo.setResizeMode(QLayout.Minimum);
    self.editor = LogEntryEditor(self);
    self.connect(self.editor,PYSIGNAL("filesSelected()"),self,PYSIGNAL("filesSelected()"));
    lo.addWidget(self.editor);
    lo.addSpacing(5);
    # create button bar
    btnfr = QFrame(self);
    btnfr.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
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
    self.setMinimumSize(256,512);
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
#    if updated:
#      self._has_tip = """<P>This dialog popped up because new data products
#        have been detected and pounced on. If you dislike this behaviour, disable the
#        "pounce" option in the main PURR window.<P>""";
    return updated;
  
  def suggestTitle(self,title):
    self.editor.suggestTitle(title);
    
  def addComment(self,comment):
    self.editor.addComment(comment);
    
  def setDefaultDirs (self,*dirs):
    self.editor.setDefaultDirs(*dirs);
    
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
    
