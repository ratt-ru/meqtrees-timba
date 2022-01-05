#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
#% $Id: tdlgui.py 6822 2009-03-03 15:13:52Z oms $
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation &
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import Timba
from Timba.dmi import *
from Timba.utils import *
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import app_proxy_gui
from Timba.Meq import meqds
from Timba import TDL
import Timba.TDL.Settings
import Timba.TDL.Compile
from Timba.TDL import TDLOptions

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL,BusyIndicator

import imp
import sys
import re
import traceback
import os
import os.path
import tempfile

_dbg = verbosity(0,name='tdlgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

def _file_mod_time (path):
  try:
    return os.stat(path).st_mtime;
  except IOError:
    return None;

# this is information about ourselves
_MODULE_FILENAME = Timba.utils.extract_stack()[-1][0];
_MODULE_DIRNAME = os.path.dirname(_MODULE_FILENAME);

from .TDLErrorFloat import TDLErrorFloat
from .TDLOptionsDialog import TDLOptionsDialog

class TDLEditor (QFrame,PersistentCurrier):
  SupportsLineNumbers = False;

  # a single editor always has the focus
  current_editor = None;

  # flag: sync to external editor
  external_sync = True;
  def set_external_sync (value):
    global _external_sync;
    _external_sync = value;
  set_external_sync = staticmethod(set_external_sync);

  def __init__ (self,parent,close_button=False,error_window=None):
    QFrame.__init__(self,parent);
    self._enabled = True;
    toplo = QVBoxLayout(self);
    toplo.setContentsMargins(0,0,0,0);
    toplo.setSpacing(0);

    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    splitter = QSplitter(Qt.Vertical,self);
    toplo.addWidget(splitter);
    splitter.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    splitter.setChildrenCollapsible(False);

    # figure out our app_gui parent
    self._appgui = app_proxy_gui.appgui(parent);

    # create an editor box
    editor_box = QFrame(splitter);
    lo = QVBoxLayout(editor_box);
    lo.setContentsMargins(0,0,0,0);
    lo.setSpacing(0);

    # find main window to associate our toolbar with
    mainwin = parent;
    while mainwin and not isinstance(mainwin,QMainWindow):
      mainwin = mainwin.parent();

    self._toolbar = QToolBar(mainwin or self);
    lo.addWidget(self._toolbar);
    self._toolbar.setIconSize(QSize(16,16));

    #### populate toolbar

    # Exec button and menu
    self._tb_tdlexec = QToolButton(self._toolbar);
    self._toolbar.addWidget(self._tb_tdlexec);
    self._tb_tdlexec.setIcon(pixmaps.gear.icon());
    self._tb_tdlexec.setText("Exec");
    self._tb_tdlexec.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    self._tb_tdlexec.setToolTip("Accesses run-time options & jobs defined by this TDL script");
    self._tb_tdlexec.hide();

    jobs = self._tdlexec_menu = TDLOptionsDialog(self);
    jobs.setWindowTitle("TDL Jobs & Runtime Options");
    jobs.setWindowIcon(pixmaps.gear.icon());
    jobs.hide();
    QObject.connect(self._tb_tdlexec,SIGNAL("clicked()"),jobs.exec_);

    # save menu and button
    self._tb_save = QToolButton(self._toolbar);
    self._toolbar.addWidget(self._tb_save);
    self._tb_save.setIcon(pixmaps.file_save.icon());
    self._tb_save.setToolTip("Saves script. Click on the down-arrow for other options.");

    savemenu = QMenu(self);
    self._tb_save.setMenu(savemenu);
    self._tb_save.setPopupMode(QToolButton.MenuButtonPopup);
    self._tb_save._modified_color = QColor("yellow");
    qa_save = savemenu.addAction(pixmaps.file_save.icon(),"&Save script",self._save_file);
    qa_save.setShortcut(Qt.ALT+Qt.Key_S);
    QObject.connect(self._tb_save,SIGNAL("clicked()"),self._save_file);
    qa_save_as = savemenu.addAction(pixmaps.file_save.icon(),"Save script &as...",
                                     self.curry(self._save_file,save_as=True));
    qa_revert = self._qa_revert = savemenu.addAction("Revert to saved",self._revert_to_saved);

    # run menu and button

    self._qa_run = self._toolbar.addAction(pixmaps.blue_round_reload.icon(),
                              "&Save & reload",self._import_main_file);
    self._qa_run.setShortcut(Qt.ALT+Qt.Key_R);

    # Compile-time options and menu
    self._tb_opts = QToolButton(self._toolbar);
    self._toolbar.addWidget(self._tb_opts);
    self._tb_opts.setIcon(pixmaps.wrench.icon());
    self._tb_opts.setText("Options");
    self._tb_opts.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    self._tb_opts.setToolTip("Accesses compile-time options for this TDL script");
    # self._tb_opts.hide();

    opts = self._options_menu = TDLOptionsDialog(self,ok_label="Compile",ok_icon=pixmaps.blue_round_reload);
    opts.setWindowTitle("TDL Compile-time Options");
    opts.setWindowIcon(pixmaps.wrench.icon());
    QObject.connect(opts,PYSIGNAL("accepted()"),self._compile_main_file);
    QObject.connect(TDLOptions.OptionObject,SIGNAL("mandatoryOptionsSet"),self.mark_mandatory_options_set);
    opts.hide();
    QObject.connect(self._tb_opts,SIGNAL("clicked()"),opts.show);
    # cross-connect the rereshProfiles() signals, so that dialogs can update each other's
    # profile menus
    QObject.connect(self._options_menu,PYSIGNAL("refreshProfiles()"),self._tdlexec_menu.refresh_profiles);
    QObject.connect(self._tdlexec_menu,PYSIGNAL("refreshProfiles()"),self._options_menu.refresh_profiles);

    self._toolbar.addSeparator();

    # cursor position indicator
    self._poslabel = QLabel(self._toolbar);
    #wa = QWidgetAction(self._toolbar);
    #wa.setDefaultWidget(self._poslabel);
    #self._toolbar.addAction(wa);
    #self._toolbar.addWidget(self._poslabel);
    self._toolbar.addWidget(self._poslabel);
    width = self._poslabel.fontMetrics().width("L:999 C:999");
    self._poslabel.setMinimumWidth(width);
    self._poslabel.setText("L:0 C:0");

    # filename indicator
    self._pathlabel = QLabel(self._toolbar);
    #wa = QWidgetAction(self._toolbar);
    #wa.setDefaultWidget(self._pathlabel);
    self._toolbar.addWidget(self._pathlabel);
    #self._toolbar.addAction(wa);
    self._pathlabel.show();
    self._pathlabel.setAlignment(Qt.AlignRight|Qt.AlignVCenter);
    self._pathlabel.setIndent(10);
    self._pathlabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    if close_button:
      if not isinstance(close_button,QIcon):
        close_button = pixmaps.remove.icon();
      self._qa_close = self._toolbar.addAction(close_button,"&Close file",self._file_closed);
      self._qa_close.setShortcut(Qt.ALT+Qt.Key_W);
    self._pathlabel.setText("(no file)");

    #### add editor window

    self._editor = editor = QTextEdit(editor_box);
    lo.addWidget(self._editor);
    editor.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    editor.setAcceptRichText(False);
    editor.setLineWrapMode(QTextEdit.NoWrap);
    self._document = QTextDocument(self);
    editor.setDocument(self._document);
    QObject.connect(self._document,SIGNAL("modificationChanged(bool)"),self._text_modified);
    QObject.connect(self._editor,SIGNAL("cursorPositionChanged()"),self._display_cursor_position);
    # QObject.connect(self._editor,SIGNAL("textChanged()"),self._clear_transients);

    # add character formats for error display
    self._format_error = QTextCharFormat(self._editor.currentCharFormat());
    self._format_error.setBackground(QBrush(QColor("lightpink")));
    self._format_suberror = QTextCharFormat(self._editor.currentCharFormat());
    self._format_suberror.setBackground(QBrush(QColor("lightgrey")));
    self._format_current_error = QTextCharFormat(self._editor.currentCharFormat());
    self._format_current_error.setBackground(QBrush(QColor("orangered")));

    # add message window
    self._message_box = QFrame(editor_box);
    lo.addWidget(self._message_box);
    self._message_box.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    self._message_box.setFrameStyle(QFrame.Panel+QFrame.Sunken);
    self._message_box.setLineWidth(2);
    mblo = QVBoxLayout(self._message_box);
    mblo.setContentsMargins(0,0,0,0);
    msgb1 = QHBoxLayout();
    mblo.addLayout(msgb1);
    msgb1.setContentsMargins(0,0,0,0);
    msgb1.setSpacing(0);
    self._message_icon = QToolButton(self._message_box);
    msgb1.addWidget(self._message_icon);
    self._message = QLabel(self._message_box);
    msgb1.addWidget(self._message);
    self._message.setTextFormat(Qt.RichText);
    self._message.setWordWrap(True);
    self._message.setMargin(0);
    self._message.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    # self._message_icon.setAlignment(Qt.AlignTop);
    # self._message_icon.setMargin(4);
    self._message_icon.setAutoRaise(True);
    self._message_icon.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed);
    QObject.connect(self._message_icon,SIGNAL("clicked()"),self.clear_message);
    self._message_icon.setToolTip("Click here to clear the message");
    self._message_widgets = [];
    self._message_transient = False;

    # figure out if we already have an error box to attach to
    self._error_window = error_window or getattr(parent,'_tdlgui_error_window',None);
    if self._error_window:
      #self._resize_errwin = False;
      pass;
    else:
      # otherwise create an error floater
      self._error_window = TDLErrorFloat(parent);
      setattr(parent,'_tdlgui_error_window',self._error_window);
      # self._resize_errwin = True;
    QObject.connect(self._error_window,PYSIGNAL("hasErrors()"),self._reset_errors);
    QObject.connect(self._error_window,PYSIGNAL("showError()"),self.show_error);

    # set filename
    self._filename = None;       # "official" path of file (None if new script not yet saved)
    self._mainfile = None;       # if not None, then we're "slaved" to a main file (see below)
    self._file_disktime = None;  # modtime on disk when file was loaded
    self._basename = None;
    self._modified = False;
    self._closed = False;
    self._error_at_line = {};
    self._is_tree_in_sync = True;
    self._pub_nodes = None;

  def __del__ (self):
    self.has_focus(False);

  def disable_editor (self):
    """Called before disabling the editor, as on some versions of PyQt
    the object is not destroyed properly and keeps receving signals""";
    self._enabled = False;
    QObject.disconnect(TDLOptions.OptionObject,SIGNAL("mandatoryOptionsSet"),self.mark_mandatory_options_set);

  def show_compile_options (self):
    self._options_menu.show();

  def mark_mandatory_options_set (self,enabled):
    self._options_menu.enableOkButton(enabled);

  def show_runtime_options (self):
    self._tdlexec_menu.show();

  def tree_is_in_sync (self,sync=True):
    """Tells the editor wheether the current tree is in sync with the content of the script.
    This is indicated by a visual cue on the toolbar.
    """;
    if sync:
      self._tb_tdlexec.setIcon(pixmaps.gear.icon());
      self._tb_tdlexec.setToolTip("Access run-time options & jobs defined by this TDL script");
    else:
      self._tb_tdlexec.setIcon(pixmaps.exclaim_yellow_warning.icon());
      self._tb_tdlexec.setToolTip("""Access run-time options & jobs defined by this TDL script.
Warning! You have modified the script since it was last compiled, so the tree may be out of date.""");

  def _file_closed (self):
    self.emit(PYSIGNAL("fileClosed()"),self);

  def hideEvent (self,ev):
    self.emit(PYSIGNAL("hidden()"));
    self.emit(PYSIGNAL("visible()"),False);
    return QFrame.hideEvent(self,ev);

  def showEvent (self,ev):
    self.emit(PYSIGNAL("shown()"));
    self.emit(PYSIGNAL("visible()"),True);
    return QFrame.showEvent(self,ev);

  def hide_jobs_menu (self,dum=False):
    if self._closed:
      return;
    self._tb_tdlexec.hide();
    self.clear_message();

  def show_line_numbers (self,show):
    pass;

  def show_run_control (self,show=True):
    if self._closed:
      return;
    self._qa_run.setVisible(show);

  def enable_controls (self,enable=True):
    if self._closed:
      return;
    self._qa_run.setEnabled(enable);
    self._tb_tdlexec.setEnabled(enable);
    if not enable:
      self.clear_message();

  def disable_controls (self,disable=True):
    if self._closed:
      return;
    self._qa_run.setDisabled(disable);
    self._tb_tdlexec.setDisabled(disable);
    if disable:
      self.clear_message();

  def get_filename (self):
    return self._filename;
  def get_mainfile (self):
    return self._mainfile;

  def _import_main_file (self):
    # self._tb_opts.setOn(False);
    self.clear_errors();
    if self._document.isModified():
      self._save_file();
    self.emit(PYSIGNAL("importFile()"),self,self._mainfile or self._filename);

  def _compile_main_file (self):
    # self._tb_opts.setOn(False);
    self.clear_errors();
    if self._document.isModified():
      self._save_file();
    self.emit(PYSIGNAL("compileFile()"),self,self._mainfile or self._filename);

  def _clear_transients (self):
    """if message box contains a transient message, clears it""";
    if self._message_transient:
      self.clear_message();

  def _display_cursor_position (self):
    cursor = self._editor.textCursor();
    pos = cursor.position();
    col = cursor.columnNumber();
    line = cursor.blockNumber();
    self._poslabel.setText("L:<b>%d</b> C:<b>%d</b>" % (line+1,col+1));
    self._poslabel.repaint();


  def _text_modified (self,mod=True):
    self._modified = mod;
    self.emit(PYSIGNAL("textModified()"),self,bool(mod));
    self._tb_save.setAutoRaise(not mod);
    self._qa_revert.setEnabled(mod);
    #if mod:
      #self._tb_save.setBackgroundRole(QPalette.ToolTipBase);
    #else:
      #self._tb_save.setBackgroundRole(QPalette.Button);
    if self._filename:
      label = '<b>' + self._basename + '</b>';
      self._pathlabel.setToolTip(self._filename);
    else:
      label = '';
      self._pathlabel.setToolTip('');
    if self._readonly:
      label = '[r/o] ' + label;
    if mod:
      self._clear_transients();
      label = '[mod] ' + label;
    self._pathlabel.setText(label);

  def clear_message (self):
    # traceback.print_stack();
    self._message_box.hide();
    self._message.setText('');
    self._message_icon.setText('');
    self._message_transient = False;
    if self._message_widgets:
      dum = QWidget();
      for w in self._message_widgets:
        w.reparent(dum);
      self._message_widgets = [];

  def show_message (self,msg,error=False,icon=None,transient=False):
    """Shows message in box.
    If icon is not None, overrides standard icon.
    If error=True, uses error icon (icon overrides this).
    If transient=True, message will be cleared when text is edited.
    """;
    self._message.setText(msg);
    if not icon:
      if error:
        icon = pixmaps.red_round_cross.icon();
      else:
        icon = pixmaps.info_blue_round.icon();
    self._message_icon.setIcon(icon);
    self._message_box.show();
    self._message_transient = transient;
    self.clear_errors();

  def messagebox ():
    return self._message_box;

  def add_message_widget (self,widget):
    self._mblo.addWidget(widget);
    self._message_widgets.append(widget);

  def clear_errors (self):
    self._error_window.clear_errors(emit_signal=True);

  def _find_block_by_linenumber (self,line):
    block = block0 = self._document.begin();
    nblock = 1;
    while block and nblock < line:
      block0 = block;
      block = next(block0);
      nblock += 1;
    return block or block0;

  def _reset_errors (self,nerr):
    """helper method, resets error markers and such. Usually tied to a hasErrors() signal
    from an error window""";
    if not self._enabled:
      return;
    self._error_at_line = {};
    self._error_selections = [];
    self._current_error_selection = QTextEdit.ExtraSelection();
    nerr_local = 0;
    if nerr:
      error_locations = self._error_window.get_error_locations();
      for err_num,filename,line,column,suberror in error_locations:
        if filename == self._filename:
          nerr_local += 1;
          # make cursor corresponding to line containing the error
          cursor = QTextCursor(self._find_block_by_linenumber(line));
          cursor.select(QTextCursor.LineUnderCursor);
          # make selection object
          qsel = QTextEdit.ExtraSelection();
          qsel.cursor = cursor;
          if suberror:
            qsel.format = self._format_suberror;
          else:
            qsel.format = self._format_error;
          # insert into error_at_line list
          self._error_at_line[line-1] = len(self._error_selections),cursor;
          # append to list of error selections
          self._error_selections.append(qsel);
      self._editor.setExtraSelections(self._error_selections);
    else:
      self._editor.setExtraSelections([]);
    self.emit(PYSIGNAL("hasErrors()"),self,nerr_local);

  def show_error (self,err_num,filename,line,column):
    """Shows error at the given position, but only if the filename matches.
    Can be directly connected to a showError() signal from an error window""";
    if filename == self._filename:
      errnum,cursor = self._error_at_line.get(line-1,(None,None));
      if cursor:
        # change selections
        self._current_error_selection.cursor = cursor;
        self._current_error_selection.format = self._format_current_error;
        sels = self._error_selections[:errnum] + self._error_selections[(errnum+1):];
        sels.append(self._current_error_selection);
        self._editor.setExtraSelections(sels);
        # move current cursor
        cursor = self._editor.textCursor();
        # scroll to line-1 and line+1 to make sure line is fully visible
        if line > 1:
          cursor.setPosition(self._find_block_by_linenumber(line-2).position() + column);
          self._editor.setTextCursor(cursor);
          self._editor.ensureCursorVisible();
        if line < self._document.blockCount():
          cursor.setPosition(self._find_block_by_linenumber(line).position() + column);
          self._editor.setTextCursor(cursor);
          self._editor.ensureCursorVisible();
        # finally, scroll to line
        cursor.setPosition(self._find_block_by_linenumber(line).position() + column);
        self._editor.setTextCursor(cursor);
        self._editor.ensureCursorVisible();


  def sync_external_file (self,filename=None,ask=True):
    #
    # NB: problem because it resets the errors
    filename = filename or self._filename;
    filetime = _file_mod_time(filename);
    if not filetime or filetime == self._file_disktime:
      return True;  # in sync
    if not ask:
      res = QMessageBox.Discard;
    else:
      res = QMessageBox.warning(self,"TDL file changed",
        """<p><tt>%s</tt> has been modified by another program.
        Would you like to save your changes and overwrite the version on disk,
	discard your changes and revert to the version on disk, or cancel the operation?"""
        % (filename,),QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel);
    if res == QMessageBox.Cancel:
      return None;
    elif res == QMessageBox.Discard:
      if filename != self._filename:
        self.load_file(filename,mainfile=self._mainfile);
      else:
        self.reload_file();
    return True;  # in sync

  def _save_file (self,filename=None,text=None,force=False,save_as=False):
    """Saves text. If force=False, checks modification times in case
    the file has been modified by another program.
    If force=True, saves unconditionally.
    If no filename is known, asks for one.
    Returns True if file was successfully saved, else None.""";
    filename = filename or self._filename;
    if filename and not save_as:
      if not force:
        if not self.sync_external_file(filename=filename,ask=True):
          return None;
    else: # no filename, ask for one
      try:
        dialog = self._save_as_dialog;
        dialog.setDirectory(dialog.directory());  # hopefully this rescan the directory
      except AttributeError:
        self._save_as_dialog = dialog = QFileDialog(self,"Saved TDL Script");
        dialog.resize(800,dialog.height());
        dialog.setMode(QFileDialog.AnyFile);
        dialog.setNameFilters(["TDL scripts (*.tdl *.py)","All files (*.*)"]);
        dialog.setViewMode(QFileDialog.Detail);
      if dialog.exec_() != QDialog.Accepted:
        return None;
      filename = str(dialog.selectedFiles()[0]);
    # save the file
    if text is None:
      text = str(self._editor.document().toPlainText());
    try:
      outfile = open(filename,"w").write(text);
    except IOError:
      (exctype,excvalue,tb) = sys.exc_info();
      _dprint(0,'exception',sys.exc_info(),'saving TDL file',filename);
      self.show_message("""<b>Error writing <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (filename,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
    # saved successfully, update stuff
    self._filename = filename;
    self._qa_revert.setEnabled(True);
    self._basename = os.path.basename(filename);
    self._file_disktime = _file_mod_time(filename);
    self._document.setModified(False);
    self.emit(PYSIGNAL("fileSaved()"),self,filename);
    return self._filename;

  def close (self):
    self._closed = True;

  def confirm_close (self):
    if self._document.isModified():
      res = QMessageBox.warning(self,"TDL file modified",
        """Save modified file <p><tt>%s</tt>?</p>"""
        % (self._filename or "",),QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel);
      if res == QMessageBox.Cancel:
        return False;
      if res == QMessageBox.Save:
        if not self._save_file():
          return False;
    self.close();
    return True;

  def _revert_to_saved (self,force=False):
    if not self._filename:
      return;
    if not force:
      if QMessageBox.question(self,"Revert to saved",
	  """Revert to saved version of <p><tt>%s</tt>?"""%(self._filename,),
	  QMessageBox.Ok|QMessageBox.Cancel) == QMessageBox.Cancel:
        return;
    self.load_file(self._filename,mainfile=self._mainfile);

  def _add_menu_label (self,menu,label):
    tlab = QLabel("<b>"+label+"</b>",menu);
    tlab.setAlignment(Qt.AlignCenter);
    tlab.setFrameShape(QFrame.ToolBarPanel);
    tlab.setFrameShadow(QFrame.Sunken);
    menu.insertItem(tlab);

  def has_compile_options (self):
    return self._options_menu.treeWidget().topLevelItemCount();

  def has_runtime_options (self):
    return self._tdlexec_menu.treeWidget().topLevelItemCount();

  def import_content (self,force=False,show_options=False):
    """imports TDL module but does not run _define_forest().
    Depending on autosync/modified state, asks to save or revert.
    If module is already imported, does nothing, unless force=True,
    in which case it imports unconditionally.
    If do_compile=True, proceeds to show compile-time options on success,
    or to compile directly if there are no options
    Return value:
      True on successful import
      None if cancelled by user.
    Import errors are posted to the error dialog.
    """;
    # save list of publishers (since forest will be cleared on import)
    if self._pub_nodes is None:
      if TDL.Compile.last_imported_file() == self._filename:
        self._pub_nodes = [ node.name for node in meqds.nodelist.iternodes() if node.is_publishing() ];
        _dprint(2,"last imported file matches, saving",len(self._pub_nodes),"publishers")
      else:
        self._pub_nodes = [];
        _dprint(2,"last imported file doesn't match:",TDL.Compile.last_imported_file(),self._filename)
    _dprint(1,self._filename,"importing");
    self.clear_message();
    self.clear_errors();
    self._options_menu.hide();
    self._tb_tdlexec.hide();
    self._tdlexec_menu.hide();
    # change the current directory to where the file is
    # os.chdir(os.path.dirname(self._filename));
    # The Python imp module expects text to reside in a disk file, which is
    # a pain in the ass for us if we're dealing with modified text or text
    # entered on-the-fly. So, either save or sync before proceeding
    global _external_sync;
    if self._document.isModified() or not self._filename:
      if not self._save_file():
        return None;
    else:
      if not self.sync_external_file(ask=False):
        return None;
    # if we already have an imported module and disk file hasn't changed, skip
    # the importing step
    busy = BusyIndicator();
    if force or self._tdlmod is None or self._tdlmod_filetime == self._file_disktime:
      # reset data members
      _dprint(2,self._filename,"emitting signal for 0 compile-time options");
      self.emit(PYSIGNAL("hasCompileOptions()"),self,0);
      self._options_menu.hide();
      self._options_menu.clear();
      self._tdlmod = None;
      # get text from editor
      tdltext = str(self._document.toPlainText());
      try:
        tdlmod,tdltext = TDL.Compile.import_tdl_module(self._filename,tdltext);
      # catch import errors
      except TDL.CumulativeError as value:
        _dprint(0,"caught cumulative error, length",len(value.args));
        self._error_window.set_errors(value.args,message="TDL import failed");
        busy = None;
        return None;
      except Exception as value:
        _dprint(0,"caught other error, traceback follows");
        traceback.print_exc();
        self._error_window.set_errors([value],message="TDL import failed");
        busy = None;
        return None;
      # remember module and nodescope
      self._tdlmod = tdlmod;
      self._tdltext = tdltext;
      self._tdlmod_filetime = self._file_disktime;
      # build options menu from compile-time options
      opt_tw = self._options_menu.treeWidget();
      opts = TDLOptions.get_compile_options();
      if opts:
        # add options
        try:
          TDLOptions.populate_option_treewidget(opt_tw,opts);
        except Exception as value:
          _dprint(0,"error setting up TDL options GUI");
          traceback.print_exc();
          self._error_window.set_errors([value],message="Error setting up TDL options GUI");
          busy = None;
          return None;
        # self._tb_opts.show();
        _dprint(2,self._filename,"emitting signal for",len(opts),"compile-time options");
        self.emit(PYSIGNAL("hasCompileOptions()"),self,len(opts));
    # success, show options or compile
    if show_options and self.has_compile_options():
      self._options_menu.adjustSizes();
      self._options_menu.show();
    busy = None;
    return True;

  def compile_content (self):
    # import content first, and return if failed
    if not self.import_content(force=True):
      return None;
    _dprint(1,self._filename,"compiling forest");
    # clear predefined functions
    self._tb_tdlexec.hide();
    # try the compilation
    busy = BusyIndicator();
    try:
      (_tdlmod,ns,msg) = \
	TDL.Compile.run_forest_definition(
	    meqds.mqs(),self._filename,self._tdlmod,self._tdltext,
	    parent=self,wait=False);
    # catch compilation errors
    except TDL.CumulativeError as value:
      _dprint(0,"caught cumulative error, length",len(value.args));
      self._error_window.set_errors(value.args,message="TDL import failed");
      busy = None;
      return None;
    except Exception as value:
      _dprint(0,"caught other error, traceback follows");
      traceback.print_exc();
      self._error_window.set_errors([value]);
      busy = None;
      return None;
    # refresh the nodelist
    meqds.request_nodelist(sync=True);
    # restore publishing nodes
    for name in (self._pub_nodes or []):
      if name in ns.AllNodes():
        _dprint(2,"reenabling publishing of",name);
        meqds.enable_node_publish_by_name(name,sync=True,get_state=True);
      else:
        _dprint(2,"not reenabling publishing of",name,", as it no longer exists?");
    # clear publisher list so it's re-saved next time in import_content()
    self._pub_nodes = None;
    ### NB: presume this all was successful for now
    # insert node scope into TDL module
    setattr(_tdlmod,'_tdl_nodescope',ns);

    # does the script define an explicit job list?
    joblist = getattr(_tdlmod,'_tdl_job_list',[]);
    if not joblist:
      joblist = [];
      # try to build it from implicit function names
      for (name,func) in _tdlmod.__dict__.items():
        if name.startswith("_tdl_job_") and callable(func) and not TDLOptions.is_jobfunc_defined(func):
          joblist.append(func);
    # does the script define a testing function?
    testfunc = getattr(_tdlmod,'_test_forest',None);
    if not callable(testfunc):
      testfunc = getattr(_tdlmod,'test_forest',None);
      if callable(testfunc):
        res = QMessageBox.warning(self,"Deprecated method",
          """Your script contains a test_forest() method. This is deprecated
          and will be disabled in the future. Please rename it to
          _test_forest().
          """,
          QMessageBox.Ok);
    if callable(testfunc):
      joblist.append(testfunc);
    
    from past.builtins import cmp
    from functools import cmp_to_key
    joblist.sort(key=cmp_to_key(lambda a, b: cmp(str(a), str(b))));

    # create list of job actions
    opts = TDLOptions.get_runtime_options();
    self._tdlexec_menu.clear();
    if joblist or opts:
      if opts:
        self._job_executor = curry(self.execute_tdl_job,_tdlmod,ns);
        ## new style:
        try:
          TDLOptions.populate_option_treewidget(self._tdlexec_menu.treeWidget(),opts,executor=self._job_executor);
        except Exception as value:
          _dprint(0,"error setting up TDL options GUI");
          traceback.print_exc();
          self._error_window.set_errors([value],message="Error setting up TDL options GUI");
          busy = None;
          return None;
      if joblist:
        for func in joblist:
          name = re.sub("^_tdl_job_","",func.__name__);
          name = name.replace('_',' ');
          self._tdlexec_menu.addAction(name,
              curry(self.execute_tdl_job,_tdlmod,ns,func,name,func.__name__),
              icon=pixmaps.gear);
      self.emit(PYSIGNAL("hasRuntimeOptions()"),self,True);
      self._tdlexec_menu.adjustSizes();
      self._tb_tdlexec.show();
    else:
      self.emit(PYSIGNAL("hasRuntimeOptions()"),self,False);
      self._tb_tdlexec.hide();

    if joblist:
      msg += " %d predefined function(s) available, please use the Exec menu to run them." % (len(joblist),);

    self.show_message(msg,transient=True);
    busy = None;
    return True;

  def execute_tdl_job (self,_tdlmod,ns,func,name,job_id):
    """executes a predefined TDL job given by func""";
    self._tdlexec_menu.hide();
    try:
      # log job
      TDLOptions.dump_log("running TDL job '%s' (%s)"%(name,("job id '%s'"%job_id if job_id else "no job id")));
      busy = BusyIndicator();
      func(meqds.mqs(),self);
      # no errors, so clear error list, if any
      self.clear_errors();
      self.show_message("TDL job '"+name+"' executed.",transient=True);
      busy = None;
    except:
      (etype,exc,tb) = sys.exc_info();
      _dprint(0,'exception running TDL job',func.__name__);
      traceback.print_exception(etype,exc,tb);
      # use TDL add_error() to process the error, since this automatically
      # adds location information. However, we want to remove ourselves
      # from the stack traceback first
      tb = traceback.extract_tb(tb);
      # pop everything leading up to our filename
      while tb[0][0] != _MODULE_FILENAME:
        tb.pop(0);
      # pop frame with our filename, this should leave only TDL-code frames
      tb.pop(0);
      ns.AddError(exc,tb,error_limit=None);
      msg = "TDL job '"+name+"' failed";
      self._error_window.set_errors(ns.GetErrors(),message=msg);
      self.emit(PYSIGNAL("showEditor()"),self);
      busy = None;

  def get_jobs_popup (self):
    return self._tdlexec_menu;

  def get_options_popup (self):
    return self._options_menu;

  def _set_mainfile (self,mainfile):
    """adjusts GUI controls based on whether we are a mainfile or not""";
    self._mainfile = mainfile;
    self._mainfile_base = mainfile and os.path.basename(mainfile);
    # if we have a mainfile, add extra options for the Run button
    if mainfile:
      self._qa_run.setToolTip("Saves this file and compiles the main script "+self._mainfile_base);
      self._qa_run.setText("Compile "+self._mainfile_base);
    else:
      self._qa_run.setToolTip("Saves and compiles this script.");
      self._qa_run.setText("Compile");

  def reload_file (self):
    text = open(self._filename).read();
    # set save icons, etc.
    self._qa_revert.setEnabled(True);
    self._file_disktime = _file_mod_time(self._filename);
    self._document.setPlainText(text);
    self._document.setModified(False);
    self._editor.setReadOnly(not os.access(self._filename,os.W_OK));

  def load_file (self,filename,text=None,readonly=False,mainfile=None):
    """loads editor content.
    filename is filename. text is file contents, if none then file will be re-read.
    readonly is True for readonly mode.
    If mainfile is not None, then this editor is "slaved" to the mainfile. This is the
    case for files included from other modules.
    """
    self.clear_message();
    if not os.access(filename,os.W_OK):
      readonly = True;
    # load text from file if not supplied
    if text is None:
      text = open(filename).read();
    self._filename = filename;
    # sets as as the mainfile or as a submodule of a main file
    self._set_mainfile(mainfile);
    # set save icons, etc.
    self._qa_revert.setEnabled(True);
    self._basename = os.path.basename(filename);
    self._readonly = readonly;
    self._file_disktime = filename and _file_mod_time(filename);
    self._document.setPlainText(text);
    self._document.setModified(False);
    self._editor.setReadOnly(not os.access(self._filename,os.W_OK));
    self._text_modified(False);   # to reset labels
    QApplication.processEvents(QEventLoop.ExcludeUserInputEvents);
    # emit signals
    self.emit(PYSIGNAL("fileLoaded()"),self,filename);
    # if module is a main-level file (i.e. not slaved to another mainfile),
    # pre-import it so that compile-time menus become available
    self._tdlmod = None;
    if not mainfile:
      self.import_content();

  def adjust_editor_font (self):
    pass;

  def has_focus (self,focus):
    if focus:
      TDLEditor.current_editor = self;
    else:
      if TDLEditor.current_editor == self:
        TDLEditor.current_editor = None;

