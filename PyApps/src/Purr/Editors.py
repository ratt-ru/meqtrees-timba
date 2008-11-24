from qt import *
import time
import os
import os.path
import sets

from Purr import Config,pixmaps
import Purr.LogEntry
import Purr.Render

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
    ndplv = self.wdplv = QListView(dppane);
    ndplv.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    lo_top.addWidget(self.wdplv);
    # insert columns, and numbers for them
    self.ColAction   = ndplv.columns(); ndplv.addColumn("action");
    self.ColFilename = ndplv.columns(); ndplv.addColumn("filename",120);
    self.ColRename   = ndplv.columns(); ndplv.addColumn("rename to",120);
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
    ndplv.setSelectionMode(QListView.Single);
    ndplv.header().show();
    ndplv.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    self.connect(ndplv,SIGNAL("mouseButtonClicked(int,QListViewItem*,const QPoint &,int)"),self._itemClicked);
    self.connect(ndplv,SIGNAL("itemRenamed(QListViewItem*,int)"),self._itemRenamed);
    self.connect(ndplv,SIGNAL('contextMenuRequested(QListViewItem*,const QPoint &,int)'),
                     self._showItemContextMenu);
    # create popup menu for existing DPs
    self._archived_dp_menu = menu = QPopupMenu();
    qa = QAction(pixmaps.editcopy.iconset(),"Restore file from this entry's archived copy",0,menu);
    QObject.connect(qa,SIGNAL("activated()"),self._restoreItemFromArchive);
    qa.addTo(self._archived_dp_menu);
    qa = QAction(pixmaps.editpaste.iconset(),"Copy location of archived copy to clipboard",0,menu);
    QObject.connect(qa,SIGNAL("activated()"),self._copyItemToClipboard);
    qa.addTo(self._archived_dp_menu);
    self._current_item = None;
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
      
  # The keys of this dict are valid policies for new data products
  # The values are the "next" policy when cycling through
  _policy_cycle = dict(copy="move",move="ignore",ignore="banish",banish="copy");
  _policy_icons = dict(copy='copy',move='move',ignore='grey_round_cross',banish='red_round_cross');
  # The keys of this dict are valid policies for archived data products
  # The values are the "next" policy when cycling through
  _policy_cycle_archived = dict(keep="remove",remove="keep");
  _policy_icons_archived = dict(keep="checkmark",remove="grey_round_cross");
    
  def hideEvent (self,event):
    QWidget.hideEvent(self,event);
    if self._add_dp_dialog:
      self._add_dp_dialog.hide();
    
  def resetDPs (self):
    self.wdplv.clear();
    self.dpitems = {};
    self.policies_updated = False;
    
  def reset (self):
    self.resetDPs();
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
    
  def _itemClicked (self,button,item,point,column):
    if not item or button != Qt.LeftButton:
      return;
    if column == self.ColAction:
      self._setItemPolicy(item,item._policy_cycle.get(item._policy,"copy"));
      self.updated = True;
      self.policies_updated = True;
      self.emit(PYSIGNAL("updated()"),());
    elif column == self.ColRender:
      item._render = (item._render+1)%len(item._renderers);
      item.setText(self.ColRender,item._renderers[item._render]);
      self.updated = True;
      self.emit(PYSIGNAL("updated()"),());
    elif column in [self.ColRename,self.ColComment]:
      item.startRename(column);
  
  def _showItemContextMenu (self,item,point,col):
    """Callback for contextMenuRequested() signal. Pops up item menu, if defined""";
    menu = getattr(item,'_menu',None);
    if menu: 
      # self._current_item tells callbacks what item the menu was referring to
      self._current_item = item;
      self.wdplv.clearSelection();
      self.wdplv.setSelected(item,True);
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
      
  def _itemRenamed (self,item,col):
    self.updated = True;
    self.emit(PYSIGNAL("updated()"),());
      
  def _setItemPolicy (self,item,policy):
    pmname = item._policy_icons.get(policy);
    if pmname is None:
      policy = "copy";
      pmname = item._policy_icons.get(policy);
    item._policy = policy;
    item.setText(self.ColAction,policy);
    pixmap = getattr(pixmaps,pmname,None);
    if pixmap:
      item.setPixmap(self.ColAction,pixmap.pm());
    else:
      item.setPixmap(self.ColAction,QPixmap());
      
  def _makeDPItem (self,dp,after):
    item = QListViewItem(self.wdplv,after);
    item._sourcepath = dp.sourcepath;
    # setup available policies for new or archived items, set initial policy
    if dp.archived:
      item._policy_cycle = self._policy_cycle_archived;
      item._policy_icons = self._policy_icons_archived;
      self._setItemPolicy(item,"keep");
      item._dp = dp;    # indicates old DP which may be updated
      item._menu = self._archived_dp_menu;
    else:
      item._policy_cycle = self._policy_cycle;
      item._policy_icons = self._policy_icons;
      self._setItemPolicy(item,dp.policy);
      item._dp = None;  # indicates new DP needs to be created
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
      i0 = self.wdplv.firstChild();
      while i0:
        if i0._policy not in ["remove","ignore","banish"]:
          taken_names.add(str(i0.text(self.ColRename)));
        i0 = i0.nextSibling();
      # ensure uniqueness of filename
      filename = self._makeUniqueFilename(taken_names,filename);
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
    self.dpitems[item._sourcepath] = item;
    return item;
  
  def _titleChanged (self,*dum):
    self._title_changed = self.updated = True;
    self.emit(PYSIGNAL("updated()"),());
    
  def _commentChanged (self,*dum):
    self._comment_changed = self._comment_edited = self.updated = True;
    self.emit(PYSIGNAL("updated()"),());
  
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
    nrm = 0;
    item = self.wdplv.firstChild();
    while item:
      if item._policy == "remove":
        nrm += 1;
      item = item.nextSibling();
    return nrm;
      
  def _makeUniqueFilename (self,taken_names,name):
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
      
  def resolveFilenameConflicts (self,dialog=True):
    """Goes through list of DPs to make sure that their destination names
    do not clash. Applies new names. Returns True if some conflicts were resolved.
    If dialog is True, shows confirrmation dialog."""
    taken_names = sets.Set();
    resolved = False;
    item = self.wdplv.firstChild();
    # iterate through items
    while item:
      # only apply this to saved DPs
      if item._policy not in ["remove","ignore","banish"]:
        name0 = str(item.text(self.ColRename));
        name = self._makeUniqueFilename(taken_names,name0);
        if name != name0:
          item.setText(self.ColRename,name);
          resolved = True;
      item = item.nextSibling();
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
    dps = [];
    # if editing existing entry, build list of archived DPs first
    if self.entry is not None:
      # first remove all items marked for removal, in case their names clash with
      # new or renamed items
      for item,dp in zip(self._dpitem_list,self.entry.dps):
        if item and item._policy == "remove":
          dp.remove_file();
          dp.remove_subproducts();
      # now go and change remaining items
      for item,dp in zip(self._dpitem_list,self.entry.dps):
        if item and item._policy != "remove":
          dp.render  = str(item.text(self.ColRender));
          dp.comment = str(item.text(self.ColComment));
          dp.rename(str(item.text(self.ColRename)));
          dps.append(dp);
    # now, append any new DPs from items (for new entries, all DPs will be new)
    item = self.wdplv.firstChild();
    while item:
      if item._dp is None: # None means a new DP
        dps.append(Purr.DataProduct(sourcepath=item._sourcepath,policy=item._policy,
                                    filename=str(item.text(self.ColRename)),
                                    render=str(item.text(self.ColRender)),
                                    comment=str(item.text(self.ColComment))));
      item = item.nextSibling();
    # update or return new entry
    if self.entry:
      self.entry.update(title=title,comment=comment,dps=dps);
      self.entry.save();
      return self.entry;
    else:
      return Purr.LogEntry(time.time(),title,comment,dps);
    
  def updateIgnoredEntry (self):
    # now, append any new DPs from items (for new entries, all DPs will be new)
    item = self.wdplv.firstChild();
    dps = [];
    while item:
      if item._dp is None: # None means a new DP
        # set all policies to ignore, unless already set to banish
        if item._policy != "banish":
          self._setItemPolicy(item,"ignore");
        dps.append(Purr.DataProduct(sourcepath=item._sourcepath,policy=item._policy,
                                    comment=str(item.text(self.ColComment))));
      item = item.nextSibling();
    # return new entry
    return Purr.LogEntry(time.time(),dps=dps,ignore=True);
    
  def setEntry (self,entry=None):
    """Populates the dialog with contents of an existing entry.""";
    busy = Purr.BusyIndicator();
    self.entry = entry;
    self.setEntryTitle(entry.title);
    self.setEntryComment(entry.comment.replace("\n","\n\n"));
    self.wdplv.clear();
    self.dpitems = {};
    # this will be a parallel list of items corresponding to each DP
    # with None for ignored DPs (since they don't appear in the list when editing old entries)
    self._dpitem_list = [];
    item = None;
    # non-ignored items first
    for dp in entry.dps:
      if not dp.ignored:
        item = self._makeDPItem(dp,item);
      else:
        item = None;
      self._dpitem_list.append(item);
    self.setTimestamp(entry.timestamp);
    self.updated = False;
  
  def addDataProducts(self,dps):
    """Adds data products to dialog.
      dps is a list of DP objects
    """;
    # this flag will be set if any new non-quiet dps are added, or if existing
    # non-quiet dps (that have been checked on) are updated
    busy = Purr.BusyIndicator();
    updated = False;
    for dp in dps:
      item = self.dpitems.get(dp.sourcepath);
      if not item:
        # ignore DPs added to end, non-ignored added to head
        if dp.policy == "ignore":
          after = self.wdplv.lastItem();
        else:
          after = None;
        item = self._makeDPItem(dp,after);
      updated = updated or not (dp.ignored or dp.quiet);
    return updated;
  
  def dropDataProducts (self,*pathnames):
    """Drops new (i.e. non-archived) DP items matching the given pathnames.""";
    trash = QListView(None);
    for path in pathnames:
      item = self.dpitems.get(path,None);
      # _dp=None indicates a non-archived data product, so we can remove it
      if item and item._dp is None:
        self.wdplv.takeItem(item);
        trash.insertItem(item);
  
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
    self.ignorebtn = QPushButton(pixmaps.grey_round_cross.iconset(),"Ignore all",btnfr);
    self.ignorebtn.setEnabled(False);
    QToolTip.add(self.ignorebtn,"""<P>Tells PURR to ignore all listed data products. PURR
      will not pounce on these files again until they have been modified.<P>""");
    cancelbtn = QPushButton(pixmaps.red_round_cross.iconset(),"Cancel",btnfr);
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
    # add entry
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
    
