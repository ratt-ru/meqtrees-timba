from qt import *
import time
import os
import os.path
import sets

from Purr import Config,pixmaps
import Purr.LogEntry
import Purr.Render

def _makeUniqueFilename (taken_names,name):
  """Helper function. Checks if name is in the set 'taken_names'.
  If so, attepts to form up an untaken name (by adding numbered suffixes).
  Adds name to taken_names.
  """
  if name in taken_names:
    # try to form up new name
    basename,ext = os.path.splitext(name);
    num = 1;
    name = "%s-%d%s"%(basename,num,ext);
    while name in taken_names:
      num += 1;
      name = "%s-%d%s"%(basename,num,ext);
  # finally, enter name into set
  taken_names.add(name);
  return name;

class DPListView (QListView):
  """This class implements a QListView for data products.
  """;
  def __init__ (self,*args):
    QListView.__init__(self,*args);
    # insert columns, and numbers for them
    self.ColAction   = self.columns(); self.addColumn("action");
    self.ColFilename = self.columns(); self.addColumn("filename",120);
    self.ColRename   = self.columns(); self.addColumn("rename to",120);
    self.ColRender   = self.columns(); self.addColumn("render");
    self.ColComment  = self.columns(); self.addColumn("comment");
    self.setColumnAlignment(self.ColAction,Qt.AlignHCenter);
    self.setColumnAlignment(self.ColFilename,Qt.AlignRight);
    self.setColumnAlignment(self.ColRename,Qt.AlignRight);
    self.setColumnAlignment(self.ColRender,Qt.AlignHCenter);
    self.setColumnAlignment(self.ColComment,Qt.AlignLeft);
    self.setSorting(-1);
    # sort out resizing modes
    self.header().setMovingEnabled(False);
    self.header().setResizeEnabled(False,self.ColAction);
    self.header().setResizeEnabled(False,self.ColRender);
    self.setResizeMode(QListView.LastColumn);
    # setup other properties of the listview
    self.setAcceptDrops(True);
    self.setAllColumnsShowFocus(True);
    self.setShowToolTips(True); 
    self.setDefaultRenameAction(QListView.Accept); 
    self.setSelectionMode(QListView.Single);
    self.header().show();
    self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    self.connect(self,SIGNAL("mouseButtonClicked(int,QListViewItem*,const QPoint &,int)"),self._itemClicked);
    self.connect(self,SIGNAL("itemRenamed(QListViewItem*,int)"),self._itemRenamed);
    self.connect(self,SIGNAL('contextMenuRequested(QListViewItem*,const QPoint &,int)'),self._showItemContextMenu);
    self.connect(self,PYSIGNAL("droppedFiles()"),self,PYSIGNAL("filesSelected()"));
    # create popup menu for existing DPs
    self._archived_dp_menu = menu = QPopupMenu();
    qa = QAction(pixmaps.editcopy.iconset(),"Restore file from this entry's archived copy",0,menu);
    QObject.connect(qa,SIGNAL("activated()"),self._restoreItemFromArchive);
    qa.addTo(self._archived_dp_menu);
    qa = QAction(pixmaps.editpaste.iconset(),"Copy location of archived copy to clipboard",0,menu);
    QObject.connect(qa,SIGNAL("activated()"),self._copyItemToClipboard);
    qa.addTo(self._archived_dp_menu);
    # currently selected item
    self._current_item = None;
    # item onto which something was dropped
    self._dropped_on = None;
    # dictionary of listview items
    # key is (path,archived) tuple, value is item
    self.dpitems = {};
    
  # The keys of this dict are valid policies for new data products
  # The values are the "next" policy when cycling through
  _policy_cycle = dict(copy="move",move="ignore",ignore="banish",banish="copy");
  _policy_icons = dict(copy='copy',move='move',ignore='grey_round_cross',banish='red_round_cross');
  # The keys of this dict are valid policies for archived data products
  # The values are the "next" policy when cycling through
  _policy_cycle_archived = dict(keep="remove",remove="keep");
  _policy_icons_archived = dict(keep="checkmark",remove="grey_round_cross");
    
  def _checkDragDropEvent (self,ev):
    """Checks if event contains a file URL, accepts if it does, ignores if it doesn't""";
    # get drag text
    try:
      url = str(ev.encodedData("text/plain"));
    except:
      url = '';
    # accept event if drag text is a file URL
    if url.startswith('file://'):
      ev.accept();
      return url;
    else:
      ev.ignore();
      return None;
    
  def dragEnterEvent (self,ev):
    """Process drag-enter event. Use function above to accept or ignore it"""
    if self._checkDragDropEvent(ev):
      QListView.dragEnterEvent(self,ev);
      
  def dropEvent (self,ev):
    """Process drop event."""
    # use function above to accept event if it contains a file URL
    prefix = 'file://';
    url = self._checkDragDropEvent(ev);
    if url and url.startswith(prefix):
      # see which item the event was dropped on
      pos = self.viewport().mapFrom(self,ev.pos());
      dropitem = self.itemAt(pos);
#      print "dropped on",pos.x(),pos.y(),dropitem, \
#        dropitem and hasattr(dropitem,'_dp') and (dropitem._dp.fullpath or dropitem._dp.sourcepath);
      # url may be a list, split it up and remove 'file://' prefix
      files = [ file[len(prefix):] for file in url.split('\n')];
      # if event originated with ourselves, reorder items
      if ev.source() is self:
        self.reorderItems(dropitem,*files);
      # else event is from someone else, accept the dropped files
      else:
        self._dropped_on = dropitem;
        self.emit(PYSIGNAL("droppedFiles()"),tuple(files));
        # if event originated with another DPListView, emit a draggedAwayFiles() signal on its behalf
        if isinstance(ev.source(),DPListView):
          ev.source().emit(PYSIGNAL("draggedAwayFiles()"),tuple(files));
      
  def dragObject (self):
    """Called when a drag is started. Creates a text drag object from
    selected files.""";
    # collect list of selected files
    filelist = [];
    for item,dp in self.getItemDPList():
      if item.isSelected():
        filelist.append('file://'+(dp.fullpath or dp.sourcepath));
    # generate drag object if list is not empty
    if filelist:
      text = "\n".join(filelist);
      dobj = QTextDrag(text,self);
      return dobj;
    else:
      return None;
    
  def clear (self):
    QListView.clear(self);
    self.dpitems = {};
      
  def _setItemPolicy (self,item,policy):
    """Sets the policy of the given item""";
    pmname = item._policy_icons.get(policy);
    if pmname is None:
      policy = "copy";
      pmname = item._policy_icons.get(policy);
    item._policy = policy;
    # new DPs get their policy updated
    item.setText(self.ColAction,policy);
    pixmap = getattr(pixmaps,pmname,None);
    if pixmap:
      item.setPixmap(self.ColAction,pixmap.pm());
    else:
      item.setPixmap(self.ColAction,QPixmap());
      
  def getItemDPList (self):
    """Returns list of item,dp pairs corresponding to content of listview.
    Not-yet-saved items will have dp=None.""";
    dplist = [];
    item = self.firstChild();
    while item:
      dplist.append((item,item._dp));
      item = item.nextSibling();
    return dplist;
      
  def _makeDPItem (self,dp,after):
    """Creates listview item for data product 'dp', inserts it after item 'after'""";
    item = QListViewItem(self,after);
    item.setDragEnabled(True);
    item.setDropEnabled(True);
    item._dp = dp;
    # setup available policies for new or archived items, set initial policy
    if dp.archived:
      item._menu = self._archived_dp_menu;
      item._policy_cycle = self._policy_cycle_archived;
      item._policy_icons = self._policy_icons_archived;
      self._setItemPolicy(item,"keep");
    else:
      item._policy_cycle = self._policy_cycle;
      item._policy_icons = self._policy_icons;
      self._setItemPolicy(item,dp.policy);
    # set other columns
    item.setText(self.ColFilename,os.path.basename(dp.sourcepath));
    item.setText(self.ColComment,dp.comment or "");
    item.setRenameEnabled(self.ColRename,True);
    item.setRenameEnabled(self.ColComment,True);
    # make sure new filenames are unique
    filename = dp.filename;
    if not dp.archived:
      # form up set of taken names
      taken_names = sets.Set();
      for i0,dp0 in self.getItemDPList():
        if dp0.policy not in ["remove","ignore","banish"]:
          taken_names.add(str(i0.text(self.ColRename)));
      # ensure uniqueness of filename
      filename = _makeUniqueFilename(taken_names,filename);
    item.setText(self.ColRename,filename);
    # get list of available renderers
    item._renderers = Purr.Render.getRenderers(dp.fullpath or dp.sourcepath);
    item._render = 0;
    # for archived items, try to find renderer in list
    if dp.archived:
      try:
        item._render = item._renderers.index(dp.render);
      except:
        pass;
    item.setText(self.ColRender,item._renderers[0]);
    # add to map of items
    self.dpitems[dp.fullpath or dp.sourcepath] = item;
    return item;
    
  def _itemClicked (self,button,item,point,column):
    if not item or button != Qt.LeftButton:
      return;
    if column == self.ColAction:
      self._setItemPolicy(item,item._policy_cycle.get(item._policy,"copy"));
      self.emit(PYSIGNAL("updated()"),());
    elif column == self.ColRender:
      item._render = (item._render+1)%len(item._renderers);
      item.setText(self.ColRender,item._renderers[item._render]);
      self.emit(PYSIGNAL("updated()"),());
    elif column in [self.ColRename,self.ColComment]:
      item.startRename(column);
  
  def _itemRenamed (self,item,col):
    self.emit(PYSIGNAL("updated()"),());
  
  def _showItemContextMenu (self,item,point,col):
    """Callback for contextMenuRequested() signal. Pops up item menu, if defined""";
    menu = getattr(item,'_menu',None);
    if menu: 
      # self._current_item tells callbacks what item the menu was referring to
      self._current_item = item;
      self.clearSelection();
      self.setSelected(item,True);
      menu.exec_loop(point);
    else:
      self._current_item = None;
      
  def _copyItemToClipboard (self):
    """Callback for item menu.""";
    dp = self._current_item and getattr(self._current_item,'_dp',None);
    if dp and dp.archived:
      QApplication.clipboard().setText(dp.fullpath,QClipboard.Clipboard);
      QApplication.clipboard().setText(dp.fullpath,QClipboard.Selection);
  
  def _restoreItemFromArchive (self):
    """Callback for item menu.""";
    dp = self._current_item and getattr(self._current_item,'_dp',None);
    if dp and dp.archived:
      dp.restore_from_archive(parent=self);
        
  def reorderItems(self,beforeitem,*files):
    # determine after which item the items are to be inserted
    if beforeitem:
      after = beforeitem.itemAbove();
    else:
      after = self.lastItem();
    # move items
    for file in files:
      item = self.dpitems.get(file,None);
      if item:
        # for some reason moveItem(None) does not move to the top as I would expect,
        # so for this case some ugliness is required
        if after:
          item.moveItem(after);
        else:
          self.takeItem(item);
          self.insertItem(item);
        after = item;
        self.emit(PYSIGNAL("updated()"),());
    
  def fillDataProducts(self,dps):
    """Fills listview with existing data products""";
    after = None;
    for dp in dps:
      if not dp.ignored:
        after = self._makeDPItem(dp,after);
      
  def addDataProducts(self,dps):
    """Adds new data products to listview. dps is a list of DP objects.
    Returns True if new (non-quiet) DPs are added, or if existing non-quiet dps are updated.
    (this usually tells the main window to wake up)
    """;
    busy = Purr.BusyIndicator();
    wakeup = False;
    # if these DPs were added as a result of a drag-and-drop, we need to insert them in FRONT of the
    # dropped-on item (i.e. after the previous item)
    if self._dropped_on:
      after = item.itemAbove();
      self._dropped_on = None;
    # else insert at end (after=None)
    else:
      after = self.lastItem();
    for dp in dps:
      item = self.dpitems.get(dp.sourcepath);
      # move item if it exists
      if item:
        item.moveItem(after);
        after = item;
      # else add new item
      else:
        after = self._makeDPItem(dp,after);
      wakeup = wakeup or not (dp.ignored or dp.quiet);
    self.emit(PYSIGNAL("updated()"),());
    return wakeup;
  
  def dropDataProducts (self,*pathnames):
    """Drops new (i.e. non-archived) DP items matching the given pathnames.""";
    trash = QListView(None);
    for path in pathnames:
      item = self.dpitems.get(path);
      if item and not item._dp.archived:
        self.takeItem(item);
        trash.insertItem(item);
        del self.dpitems[path];
        self.emit(PYSIGNAL("updated()"),());
        
  def resolveFilenameConflicts (self):
    """Goes through list of DPs to make sure that their destination names
    do not clash. Adjust names as needed. Returns True if some conflicts were resolved.
    """
    taken_names = sets.Set();
    resolved = False;
    # iterate through items
    for item,dp in self.getItemDPList():
      # only apply this to saved DPs
      if dp.policy not in ["remove","ignore","banish"]:
        name0 = str(item.text(self.ColRename));
        name = _makeUniqueFilename(taken_names,name0);
        if name != name0:
          item.setText(self.ColRename,name);
          resolved = True;
          self.emit(PYSIGNAL("updated()"),());
    return resolved;
        
  def buildDPList (self):
    """Builds list of data products."""
    dps = [];
    itemlist = self.getItemDPList();
    # first remove all items marked for removal, in case their names clash with new or renamed items
    for item,dp in itemlist:
      if dp and item._policy == "remove":
        dp.remove_file();
        dp.remove_subproducts();
    # now, make list
    for item,dp in itemlist:
      if item._policy == "remove":
        continue;
      # update rendered and comment
      dp.render  = str(item.text(self.ColRender));
      dp.comment = str(item.text(self.ColComment));
      # archived DPs may need to be renamed, for new ones simply set the name
      if dp.archived:
        dp.rename(str(item.text(self.ColRename)));
      else:
        dp.set_policy(item._policy);
        dp.filename = str(item.text(self.ColRename));
      dps.append(dp);
    return dps;
      
class LogEntryEditor (QWidget):
  """This class provides a widget for editing log entries.
  """;
  def __init__ (self,parent):
    QWidget.__init__(self,parent);
    # create splitter
    lo = QVBoxLayout(self);
    self.wsplitter = QSplitter(self);
    self.wsplitter.setOrientation(Qt.Vertical);
    self.wsplitter.setChildrenCollapsible(False);
    self.wsplitter.setFrameStyle(QFrame.Box|QFrame.Raised);
    self.wsplitter.setLineWidth(2);
    lo.addWidget(self.wsplitter);
    # create pane for comment editor
    editorpane = QWidget(self.wsplitter);
    lo_top = QVBoxLayout(editorpane);
    lo_top.setResizeMode(QLayout.Minimum);
    lo_top.setMargin(5);
    # create comment editor
    # create title and timestamp label, hide timestamp until it is set (below)
    lo_topline = QHBoxLayout(lo_top);
    self.wtoplabel = QLabel("Entry title:",editorpane);
    self.wtimestamp = QLabel("",editorpane);
    lo_topline.addWidget(self.wtoplabel);
    lo_topline.addStretch(1);
    lo_topline.addWidget(self.wtimestamp);
    # add title editor
    self.wtitle   = QLineEdit(editorpane);
    lo_top.addWidget(self.wtitle); 
    self.connect(self.wtitle,SIGNAL("textChanged(const QString&)"),self._titleChanged);
    # add comment editor
    lo_top.addSpacing(5);
    lo_top.addWidget(QLabel("Comments:",editorpane));
    self.wcomment = QTextEdit(editorpane);
    self.wcomment.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self.connect(self.wcomment,SIGNAL("textChanged()"),self._commentChanged);
    lo_top.addWidget(self.wcomment);
    # generate frame for the "Data products" listview
    # lo_top.addSpacing(5);
    # create pane for comment editor
    dppane = QWidget(self.wsplitter);
    lo_top = QVBoxLayout(dppane);
    lo_top.setResizeMode(QLayout.Minimum);
    lo_top.setMargin(5);
    dpline = QWidget(dppane);
    lo_top.addWidget(dpline);
    dpline.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    lo_dpline = QHBoxLayout(dpline);
    label = QLabel("<nobr>Data products (<u><font color=blue>help</font></u>):</nobr>",dpline)
    QToolTip.add(label,self.data_product_help);
    lo_dpline.addWidget(label);
    lo_dpline.addStretch(1);
    self.wnewdp = QPushButton(pixmaps.folder_open.iconset(),"Add...",dpline);
    self.connect(self.wnewdp,SIGNAL("clicked()"),self._showAddDialog);
    self._add_dp_dialog = None;
    lo_dpline.addWidget(self.wnewdp);
    # create DP listview
    ndplv = self.wdplv = DPListView(dppane);
    ndplv.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    lo_top.addWidget(self.wdplv);
    # connect its signals
    QObject.connect(self.wdplv,PYSIGNAL("updated()"),self.setUpdated);
    QObject.connect(self.wdplv,PYSIGNAL("droppedFiles()"),self,PYSIGNAL("filesSelected()"));
    QObject.connect(self.wdplv,PYSIGNAL("draggedAwayFiles()"),self,PYSIGNAL("draggedAwayFiles()"));
    # other internal init
    self.reset();
    
  data_product_help = \
      """<P><I>Data products</I> are files that will be archived along with this log entry. If "pounce" 
      is enabled, PURR will watch your directories for new or updated files, and insert them in this list
      automatically. You can also click on "Add..." to add files by hand.</P>
      
      <P>Click on the <I>action</I> column to select what to do with a file. Click on the <I>rename</I> column 
      to archive the file under a different name. Click on the <I>comment</I> column to enter a comment for the file. Click on the <I>render</I> column to select a rendering for the file. The basic rendering is "link", which makes a simple HTML link to the archived file. Certain file types (e.g. images) may support
      more elaborate renderings.</P>
      
      <P>The meaning of the different actions is:</P>
      <DL>
      <DT><B>copy</B></DT><DD>data product will be copied to the log.</DD>
      <DT><B>move</B></DT><DD>data product will be moved to the log.</DD>
      <DT><B>ignore</B></DT><DD>data product will not appear in the log, however PURR will keep
      watching it, and will pounce on it if it changes again.</DD>
      <DT><B>banish</B></DT><DD>data product will not appear in the log, and PURR will stop
      watching it (you can un-banish a data product later by adding it via the 
      "Add..." button.)</DD>
      <DT><B>keep</B></DT><DD>(for existing products only) retain data product with this log entry.</DD>
      <DT><B>remove</B></DT><DD>(for existing products only) remove data product from this log entry.</DD>
      </DL>
      """;
      
  def hideEvent (self,event):
    QWidget.hideEvent(self,event);
    if self._add_dp_dialog:
      self._add_dp_dialog.hide();
    
  def resetDPs (self):
    self.wdplv.clear();
    
  def reset (self):
    self.wdplv.clear();
    self.entry = self._timestamp = None;
    self.wtimestamp.hide();
    self.setEntryTitle("Untitled entry");
    self.setEntryComment("No comment");
    self._default_dir = ".";
    # _title_changed is True if title was changed or edited manually
    # _comment_changed is True if comment was changed or edited manually
    # _commend_edited is True if comment was eddited since the last time something was
    #   added with addComment()
    self._title_changed = self._comment_changed = self._comment_edited = False;
    # _last_auto_comment is the last comment to have been added via addComment()
    self._last_auto_comment = None;
    self.updated = False;
    
  def setUpdated (self,updated=True):
    self.updated = updated;
    if updated:
      self.emit(PYSIGNAL("updated()"),());
    
  def setDefaultDirs (self,*dirnames):
    self._default_dirs = dirnames;
    
  class AddDataProductDialog (QFileDialog):
    """This is a file selection dialog with an extra quick-jump combobox for 
    multiple directories""";
    def __init__ (self,parent):
      QFileDialog.__init__(self);
      self.setCaption("PURR: Add Data Products");
      self.setMode(QFileDialog.ExistingFile);
      self.dirlist = None;
      # make mode selector
      wmodeselect = QButtonGroup(2,Qt.Horizontal,self);
      QRadioButton("files",wmodeselect).setChecked(True);
      QRadioButton("directories",wmodeselect);
      self.connect(wmodeselect,SIGNAL("clicked(int)"),self._setMode);
      self.addWidgets(QLabel("Select:",self),wmodeselect,None);
      # make quick-jump combobox
      self.wlabel = QLabel("Quick jump:",self);
      self.wdirlist = QComboBox(False,self);
      self.wdirlist.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
      self.connect(self.wdirlist,SIGNAL("activated(const QString &)"),self.setDir);
      self.addWidgets(self.wlabel,self.wdirlist,None);
      # connect signals (translates into a PYSIGNAL with string arguments)
      self.connect(self,SIGNAL("filesSelected(const QStringList&)"),self._filesSelected);
      self.connect(self,SIGNAL("fileSelected(const QString&)"),self._fileSelected);
      self.connect(self,SIGNAL("fileHighlighted(const QString&)"),self._fileHighlighted);
      # resize selves
      self.config_name = "add-file-dialog";
      width = Config.getint('%s-width'%self.config_name,768);
      height = Config.getint('%s-height'%self.config_name,512);
      self.resize(QSize(width,height));
      
    def resizeEvent (self,ev):
      QFileDialog.resizeEvent(self,ev);
      sz = ev.size();
      Config.set('%s-width'%self.config_name,sz.width());
      Config.set('%s-height'%self.config_name,sz.height());
      
    def show (self):
      QFileDialog.show(self);
      self._file = None;
      
    def done (self,code):
      """Workaround for QFileDialog bug: if DirctoryOnly mode, it doesn't actually emit any
      fileSelected() when OK is pressed. So we catch the selected dir via fileHighlighted() 
      below, and report it here.""";
      if code == 1 and self.mode() == QFileDialog.DirectoryOnly and self._file:
        self.emit(PYSIGNAL("filesSelected()"),(self._file,));
      QFileDialog.done(self,code);
      
    def _setMode (self,mode):
      if mode == 0:
        self.setMode(QFileDialog.ExistingFiles);
      elif mode == 1:
        self.setMode(QFileDialog.DirectoryOnly);
    
    def setDirList (self,dirlist):
      if dirlist != self.dirlist:
        self.dirlist = dirlist;
        self.wdirlist.clear();
        for dirname in dirlist:
          self.wdirlist.insertItem(dirname);
        self.wlabel.setShown(len(dirlist)>1);
        self.wdirlist.setShown(len(dirlist)>1);
          
    def _filesSelected (self,filelist):
      self.emit(PYSIGNAL("filesSelected()"),tuple(map(str,filelist)));
      
    def _fileSelected (self,file):
      self.emit(PYSIGNAL("filesSelected()"),(str(file),));
      
    def _fileHighlighted (self,file):
      self._file = str(file);
  
  def _showAddDialog (self):
    if not self._add_dp_dialog:
      self._add_dp_dialog = self.AddDataProductDialog(self);
      self.connect(self._add_dp_dialog,PYSIGNAL("filesSelected()"),
                   self,PYSIGNAL("filesSelected()"));
    # add quick-jump combobox
    self._add_dp_dialog.setDirList(self._default_dirs);
    self._add_dp_dialog.rereadDir();
    self._add_dp_dialog.show();
    self._add_dp_dialog.raiseW();
  
  def _titleChanged (self,*dum):
    self._title_changed = True;
    self.setUpdated();
    
  def _commentChanged (self,*dum):
    self._comment_changed = self._comment_edited = True;
    self.setUpdated();
  
  def suggestTitle (self,title):
    """Suggests a title for the entry.
    If title has been manually edited, suggestion is ignored.""";
    if not self._title_changed or not str(self.wtitle.text()):
      self.wtitle.setText(title);
      self._title_changed = False;
    
  def addComment (self,comment):
    # get current comment text, if nothing was changed at all, use empty text
    if self._comment_changed:
      cur_comment = str(self.wcomment.text());
      cpos = self.wcomment.getCursorPosition();
    else:
      cur_comment = "";
      cpos = None;
    # no current comments? Replace
    if not cur_comment:
      cur_comment = comment;
    # else does the comment still end with the last auto-added string? Simply
    # append our comment then
    elif self._last_auto_comment and cur_comment.endswith(self._last_auto_comment):
      cur_comment += comment;
    # else user must've edited the end of the comment. Start a new paragraph and append our
    # comment
    else:
      cur_comment += "\n\n"+comment;
    self._comment_edited = False;
    self._last_auto_comment = comment;
    # update widget
    self.wcomment.setText(cur_comment);
    if cpos:
      cpos = self.wcomment.setCursorPosition(*cpos);
    
  def countRemovedDataProducts (self):
    """Returns number of DPs marked for removal""";
    return len([item for item,dp in self.wdplv.getItemDPList() if dp.policy == "remove"]);
      
  def resolveFilenameConflicts (self,dialog=True):
    """Goes through list of DPs to make sure that their destination names
    do not clash. Applies new names. Returns True if some conflicts were resolved.
    If dialog is True, shows confirrmation dialog."""
    resolved = self.wdplv.resolveFilenameConflicts();
    if resolved and dialog:
      QMessageBox.warning(self,"Filename conflicts","""<P>
        <NOBR>PURR has found duplicate destination filenames among your data products.</NOBR> 
        This is not allowed, so some filenames have been adjusted to avoid name clashes.
        Please review the changes before saving this entry.
        </P>""",
        QMessageBox.Ok);
    return resolved;
    
  def updateEntry (self):
    """Updates entry object with current content of dialog. 
    In new entry mode (setEntry() not called, so self.entry=None), creates new entry object.
    In old entry mode (setEntry() called), updates and saves old entry object.
    """;
    # form up new entry
    title = str(self.wtitle.text());
    comment = str(self.wcomment.text());
    # process comment string -- eliminate single newlines, make double-newlines separate paragraphs
    comment = "\n".join([ pars.replace("\n"," ") for pars in comment.split("\n\n") ]);
    # go through data products and decide what to do with each one
    busy = Purr.BusyIndicator();
    # get list of DPs
    dps = self.wdplv.buildDPList();
    # emit signal for all newly-created DPs
    for dp in dps:
      if not dp.archived:
        self.emit(PYSIGNAL("creatingDataProduct()"),(dp.sourcepath,));
    # update or return new entry
    if self.entry:
      self.entry.update(title=title,comment=comment,dps=dps);
      self.entry.save();
      return self.entry;
    else:
      return Purr.LogEntry(time.time(),title,comment,dps);
    
  def updateIgnoredEntry (self):
    """Updates an ignore-entry object with current content of dialog, by
    marking all data products for ignore."""
    # collect new DPs from items 
    dps = [];
    for item,dp in self.wdplv.getItemDPList():
      if dp and not dp.archived: # None means a new DP
        # set all policies to ignore, unless already set to banish
        if dp.policy != "banish":
          self.wdplv._setItemPolicy(item,"ignore");
          dp.set_policy("ignore");
        dps.append(dp);
    # return new entry
    return Purr.LogEntry(time.time(),dps=dps,ignore=True);
    
  def setEntry (self,entry=None):
    """Populates the dialog with contents of an existing entry.""";
    busy = Purr.BusyIndicator();
    self.entry = entry;
    self.setEntryTitle(entry.title);
    self.setEntryComment(entry.comment.replace("\n","\n\n"));
    self.wdplv.clear();
    self.wdplv.fillDataProducts(entry.dps);
    self.setTimestamp(entry.timestamp);
    self.updated = False;
  
  def addDataProducts(self,dps):
    """Adds data products to dialog.
      dps is a list of DP objects
    """;
    return self.wdplv.addDataProducts(dps);
  
  def dropDataProducts (self,*pathnames):
    """Drops new (i.e. non-archived) DP items matching the given pathnames.""";
    return self.wdplv.dropDataProducts(*pathnames);
  
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
    self.setCaption("Adding Log Entry");
    self.setIcon(pixmaps.purr_logo.pm());
    self.setModal(False);
    # create pop-up tip
    self._has_tip = None;
    self._dialog_tip = self.DialogTip(self);
    # create editor
    lo = QVBoxLayout(self);
    lo.setResizeMode(QLayout.Minimum);
    self.editor = LogEntryEditor(self);
    self.dropDataProducts = self.editor.dropDataProducts;
    self.connect(self.editor,PYSIGNAL("filesSelected()"),self,PYSIGNAL("filesSelected()"));
    # connect draggedAwayFiles() signal so that files dragged away are removed from
    # the list
    self.connect(self.editor,PYSIGNAL("draggedAwayFiles()"),self.editor.dropDataProducts);
    lo.addWidget(self.editor);
    lo.addSpacing(5);
    # create button bar
    btnfr = QFrame(self);
    btnfr.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    btnfr.setMargin(5);
    lo.addWidget(btnfr);
    lo.addSpacing(5);
    btnfr_lo = QHBoxLayout(btnfr);
    newbtn = QPushButton(pixmaps.filesave.iconset(),"Add new entry",btnfr);
    QToolTip.add(newbtn,"""<P>Saves new log entry, along with any data products not marked
      as "ignore" or "banish".<P>""");
    self.ignorebtn = QPushButton(pixmaps.red_round_cross.iconset(),"Ignore all",btnfr);
    self.ignorebtn.setEnabled(False);
    QToolTip.add(self.ignorebtn,"""<P>Tells PURR to ignore all listed data products. PURR
      will not pounce on these files again until they have been modified.<P>""");
    cancelbtn = QPushButton(pixmaps.grey_round_cross.iconset(),"Hide",btnfr);
    QToolTip.add(cancelbtn,"""<P>Hides this dialog.<P>""");
    QObject.connect(newbtn,SIGNAL("clicked()"),self.addNewEntry);
    QObject.connect(self.ignorebtn,SIGNAL("clicked()"),self.ignoreAllDataProducts);
    QObject.connect(cancelbtn,SIGNAL("clicked()"),self.hide);
    btnfr_lo.setMargin(5);
    btnfr_lo.addWidget(newbtn,2);
    btnfr_lo.addStretch(1);
    btnfr_lo.addWidget(self.ignorebtn,2);
    btnfr_lo.addStretch(1);
    btnfr_lo.addWidget(cancelbtn,2);
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
    self.ignorebtn.setEnabled(True);
    return updated;
  
  def suggestTitle(self,title):
    self.editor.suggestTitle(title);
    
  def addComment(self,comment):
    self.editor.addComment(comment);
    
  def setDefaultDirs (self,*dirs):
    self.editor.setDefaultDirs(*dirs);
    
  def ignoreAllDataProducts (self):
    # confirm with user
    if QMessageBox.question(self,"Ignoring all data products","""<P><NOBR>Do you really
          want to ignore all data products</NOBR> listed here? PURR will ignore these
          files until they have been modified again.""",
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    # add ingore entry, which will store info on all ignored data products
    entry = self.editor.updateIgnoredEntry();
    self.emit(PYSIGNAL("newLogEntry()"),(entry,));
    self.editor.resetDPs();
    self.hide();
    
  def addNewEntry (self):
    # if some naming conflicts have been resolved, return -- user will need to re-save
    if self.editor.resolveFilenameConflicts():
      return;
    # confirm with user
    if QMessageBox.question(self,"Adding new entry","""<P><NOBR>Do you really want to add
          a new log entry</NOBR> titled "%s"?"""%(self.editor.entryTitle()),
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    # add entry
    entry = self.editor.updateEntry();
    self.emit(PYSIGNAL("newLogEntry()"),(entry,));
    self.editor.reset();
    self.hide();
    
class ExistingLogEntryDialog (QDialog):
  def __init__ (self,parent,*args):
    QDialog.__init__(self,parent,*args);
    self.setModal(False);
    # make stack for viewer and editor components
    lo = QVBoxLayout(self);
    self.wstack = QWidgetStack(self);
    lo.addWidget(self.wstack);
    self.wstack.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    # make editor panel
    self.editor_panel = QWidget(self.wstack);
    self.editor_panel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self.wstack.addWidget(self.editor_panel);
    lo = QVBoxLayout(self.editor_panel);
    # create editor
    self.editor = LogEntryEditor(self.editor_panel);
    self.connect(self.editor,PYSIGNAL("updated()"),self._entryUpdated);
    self.connect(self.editor,PYSIGNAL("filesSelected()"),self,PYSIGNAL("filesSelected()"));
    self.connect(self.editor,PYSIGNAL("creatingDataProduct()"),
                 self,PYSIGNAL("creatingDataProduct()"));
    lo.addWidget(self.editor);
    self.dropDataProducts = self.editor.dropDataProducts;
    # create button bar for editor
    btnfr = QFrame(self.editor_panel);
    btnfr.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    btnfr.setMargin(5);
    lo.addWidget(btnfr);
    lo.addSpacing(5);
    btnfr_lo = QHBoxLayout(btnfr);
    self.wsave = QPushButton(pixmaps.filesave.iconset(),"Save",btnfr);
    QObject.connect(self.wsave,SIGNAL("clicked()"),self._saveEntry);
    cancelbtn = QPushButton(pixmaps.grey_round_cross.iconset(),"Cancel",btnfr);
    QObject.connect(cancelbtn,SIGNAL("clicked()"),self._cancelEntry);
    btnfr_lo.setMargin(5);
    btnfr_lo.addWidget(self.wsave,1);
    btnfr_lo.addStretch(1);
    btnfr_lo.addWidget(cancelbtn,1);
    
    # create viewer panel
    self.viewer_panel = QWidget(self.wstack);
    self.viewer_panel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self.wstack.addWidget(self.viewer_panel);
    lo = QVBoxLayout(self.viewer_panel);
    label = QLabel("""<P>Below is an HTML rendering of your log entry. Note that this window 
      is only a bare-bones viewer, not a real browser. You can't click on links! To get access
      to this entry's data products, click the Edit button below.
      </P>""",self.viewer_panel);
    label.setMargin(5);
    lo.addWidget(label);
    self.viewer = QTextEdit(self.viewer_panel);
    self.viewer.setReadOnly(True);
    self.viewer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    # make a QMimeSourceFactory for the viewer -- needed to resolve image links
    self.viewer_msf = QMimeSourceFactory();
    self.viewer.setMimeSourceFactory(self.viewer_msf);
    lo.addWidget(self.viewer);
    lo.addSpacing(5);
    # create button bar
    btnfr = QFrame(self.viewer_panel);
    btnfr.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    btnfr.setMargin(5);
    lo.addWidget(btnfr);
    lo.addSpacing(5);
    btnfr_lo = QHBoxLayout(btnfr);
    btnfr_lo.setMargin(5);
    btn = self.wprev = QPushButton(pixmaps.previous.iconset(),"Previous",btnfr);
    QObject.connect(btn,SIGNAL("clicked()"),self,PYSIGNAL("previous()"));
    btnfr_lo.addWidget(btn,1);
    btnfr_lo.addSpacing(5);
    btn = self.wnext = QPushButton(pixmaps.next.iconset(),"Next",btnfr);
    QObject.connect(btn,SIGNAL("clicked()"),self,PYSIGNAL("next()"));
    btnfr_lo.addWidget(btn,1);
    btnfr_lo.addSpacing(5);
    btn = self.wedit = QPushButton(pixmaps.edit.iconset(),"Edit",btnfr);
    QObject.connect(btn,SIGNAL("clicked()"),self._editEntry);
    btnfr_lo.addWidget(btn,1);
    btnfr_lo.addStretch(1)
    btn = self.wclose = QPushButton(pixmaps.grey_round_cross.iconset(),"Close",btnfr);
    QObject.connect(btn,SIGNAL("clicked()"),self.hide);
    btnfr_lo.setMargin(5);
    btnfr_lo.addWidget(btn,1);
    
    # resize selves
    width = Config.getint('entry-viewer-width',256);
    height = Config.getint('entry-viewer-height',512);
    self.resize(QSize(width,height));
    # other init
    self.entry = None;
    self.updated = False;
    
  def resizeEvent (self,ev):
    QDialog.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('entry-viewer-width',sz.width());
    Config.set('entry-viewer-height',sz.height());
    
  def viewEntry (self,entry,has_prev=True,has_next=True):
    # if editing previous entry, ask for confirmation
    if self.updated:
      self.show();
      self._saveEntry();
    busy = Purr.BusyIndicator();
    self.entry = entry;
    self.updated = False;
    self.setCaption(entry.title);
    self.viewer_msf.setFilePath(QStringList(entry.pathname));
    self.viewer.setText(file(self.entry.index_file).read());
    self.wprev.setEnabled(has_prev);
    self.wnext.setEnabled(has_next);
    self.wstack.raiseWidget(self.viewer_panel);
    
  def setDefaultDirs (self,*dirs):
    self.editor.setDefaultDirs(*dirs);
    
  def addDataProducts (self,dps):
    self.editor.addDataProducts(dps);
    self._entryUpdated();
    
  def _editEntry (self):
    self.setCaption("Editing entry");
    self.editor.setEntry(self.entry);
    self.updated = False;
    self.wsave.setEnabled(False);
    self.wstack.raiseWidget(self.editor_panel);

  def _saveEntry (self):
    # if some naming conflicts have been resolved, return -- user will need to re-save
    if self.editor.resolveFilenameConflicts():
      return;
    # ask for confirmation
    nremove = self.editor.countRemovedDataProducts();
    msg = "<P><nobr>Save changes to this log entry?</nobr></P>";
    if nremove:
      msg += "<P>%d archived data product(s) will be removed.</P>"%nremove;
    if QMessageBox.question(self,"Saving entry",msg,
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    busy = Purr.BusyIndicator();
    self.editor.updateEntry();
    self.updated = False;
    self.setCaption(self.entry.title);
    self.viewer.setText(file(self.entry.index_file).read());
    self.wstack.raiseWidget(self.viewer_panel);
    # emit signal to regenerate log
    self.emit(PYSIGNAL("entryChanged()"),(self.entry,));
    
  def _cancelEntry (self):
    if self.updated and QMessageBox.question(self,"Abandoning changes",
          "Abandon changes to this log entry?",
          QMessageBox.Yes,QMessageBox.No) != QMessageBox.Yes:
      return;
    self.setCaption(self.entry.title);
    self.wstack.raiseWidget(self.viewer_panel);
    
  def _entryUpdated (self):
    self.updated = True;
    self.wsave.setEnabled(True);
    
