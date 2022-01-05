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
from Timba import Grid
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import app_proxy_gui
from Timba.Meq import meqds
from Timba import TDL
import Timba.TDL.Settings
import Timba.TDL.Compile
from Timba.TDL import TDLOptions

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

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

# flag: sync to external editor
_external_sync = True;
def set_external_sync (value):
  global _external_sync;
  _external_sync = value;

# this is information about ourselves
_MODULE_FILENAME = Timba.utils.extract_stack()[-1][0];
_MODULE_DIRNAME = os.path.dirname(_MODULE_FILENAME);

class TDLEditor (QFrame,PersistentCurrier):
  SupportsLineNumbers = True;
  SubErrorMarker = 0;
  ErrorMarker = 1;
  CurrentErrorMarker = 2;
  # a single editor always has the focus
  current_editor = None;

  def __init__ (self,parent,close_button=False,error_window=None):
    QFrame.__init__(self,parent);
    self._enabled = True;
    toplo = QVBoxLayout(self);
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

    # find main window to associate our toolbar with
    self._toolbar = QToolBar("TDL tools",self._appgui,editor_box);
    lo.addWidget(self._toolbar);

    #### populate toolbar

    # Exec button and menu
    self._tb_jobs = QToolButton(self._toolbar);
    self._tb_jobs.setIconSet(pixmaps.gear.iconset());
    self._tb_jobs.setTextLabel("Exec");
    self._tb_jobs.setUsesTextLabel(True);
    self._tb_jobs.setTextPosition(QToolButton.BesideIcon);
    QToolTip.add(self._tb_jobs,"Access run-time options & jobs defined by this TDL script");
    self._tb_jobs.hide();
    
    jobs = self._jobmenu = TDLOptionsDialog(self);
    jobs.setCaption("TDL Jobs & Runtime Options");
    jobs.setIcon(pixmaps.gear.pm());
    jobs.hide();
    QObject.connect(self._tb_jobs,SIGNAL("clicked()"),jobs.exec_loop);

    # save menu and button
    self._tb_save = QToolButton(self._toolbar);
    self._tb_save.setIconSet(pixmaps.file_save.iconset());
    QToolTip.add(self._tb_save,"Saves script. Click on the down-arrow for other options.");
    savemenu = QPopupMenu(self);
    self._tb_save.setPopup(savemenu);
    self._tb_save.setPopupDelay(0);
    self._tb_save._modified_color = QColor("yellow");
    qa_save = QAction(pixmaps.file_save.iconset(),"&Save script",Qt.ALT+Qt.Key_S,self);
    QObject.connect(qa_save,SIGNAL("activated()"),self._save_file);
    QObject.connect(self._tb_save,SIGNAL("clicked()"),self._save_file);
    qa_save.addTo(savemenu);
    qa_save_as = QAction(pixmaps.file_save.iconset(),"Save script &as...",0,self);
    QObject.connect(qa_save_as,SIGNAL("activated()"),self.curry(self._save_file,save_as=True));
    qa_save_as.addTo(savemenu);
    qa_revert = self._qa_revert = QAction("Revert to saved",0,self);
    QObject.connect(qa_revert,SIGNAL("activated()"),self._revert_to_saved);
    qa_revert.addTo(savemenu);

    # run menu and button
    self._tb_run = QToolButton(self._toolbar);
    self._tb_run.setIconSet(pixmaps.blue_round_reload.iconset());

    self._tb_runmenu = QPopupMenu(self);
    self._tb_run.setPopup(self._tb_runmenu);
    self._tb_run.setPopupDelay(0);
    self._qa_runmain = QAction(pixmaps.blue_round_reload.iconset(),
                              "&Save & compile main script",Qt.ALT+Qt.Key_R,self);
    QObject.connect(self._qa_runmain,SIGNAL("activated()"),self._run_main_file);
    QObject.connect(self._tb_run,SIGNAL("clicked()"),self._import_main_file);
    self._qa_runmain.addTo(self._tb_runmenu);
    qa_runthis_as = QAction(pixmaps.blue_round_reload.iconset(),"Save & run this script as main script...",0,self);
    qa_runthis_as.setToolTip("Saves and recompiles this script as a top-level TDL script");
    QObject.connect(qa_runthis_as,SIGNAL("activated()"),self._import_as_main_file);
    qa_runthis_as.addTo(self._tb_runmenu);

    # Compile-time options and menu
    #self._tb_opts = QAction(pixmaps.wrench.iconset(),
                            #"Options",Qt.ALT+Qt.Key_O,self);
    #self._tb_opts.setToggleAction(True);
    #self._tb_opts.setToolTip("Access compile-time options for this TDL script");
    #self._tb_opts.addTo(self._toolbar);
    # Compile-time options and menu
    self._tb_opts = QToolButton(self._toolbar);
    self._tb_opts.setIconSet(pixmaps.wrench.iconset());
    self._tb_opts.setTextLabel("Options");
    self._tb_opts.setUsesTextLabel(True);
    self._tb_opts.setTextPosition(QToolButton.BesideIcon);
    QToolTip.add(self._tb_opts,"Access compile-time options for this TDL script");
    # self._tb_opts.hide();

    opts = self._options_menu = TDLOptionsDialog(parent,
            ok_label="Compile",ok_icon=pixmaps.blue_round_reload);
    opts.setCaption("TDL Compile-time Options");
    opts.setIcon(pixmaps.wrench.pm());
    QObject.connect(opts,PYSIGNAL("accepted()"),self._run_main_file);
    opts.hide();
    QObject.connect(self._tb_opts,SIGNAL("clicked()"),opts.show);
    
    self._qa_recompile = qa_recomp = QAction(pixmaps.blue_round_reload.iconset(),"Re&compile script to apply new options",0,self);
    qa_recomp.setToolTip("You must recompile this script for new options to take effect");
    QObject.connect(qa_recomp,SIGNAL("activated()"),self._run_main_file);

    self._toolbar.addSeparator();
    self._poslabel = QLabel(self._toolbar);
    width = self._poslabel.fontMetrics().width("L:999 C:999");
    self._poslabel.setMinimumWidth(width);
    self._pathlabel = QLabel(self._toolbar);
    self._pathlabel.setAlignment(Qt.AlignRight);
    self._pathlabel.setIndent(10);
    if close_button:
      if not isinstance(close_button,QIconSet):
        close_button = pixmaps.remove.iconset();
      self._qa_close = QAction(close_button,"&Close file",Qt.ALT+Qt.Key_W,self);
      QObject.connect(self._qa_close,SIGNAL("activated()"),self._file_closed);
      self._qa_close.addTo(self._toolbar);
    self._toolbar.setStretchableWidget(self._pathlabel);

    #### add editor window

    self._editor = QextScintilla(editor_box);
    lo.addWidget(self._editor);
    self._editor.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self._lexer = QextScintillaLexerPython(self);
    self._editor.setLexer(self._lexer);
    self._editor_fontadjust = -6;
    self.adjust_editor_font();
    self._editor.markerDefine(QextScintilla.RightTriangle,self.ErrorMarker);
    self._editor.markerDefine(QextScintilla.RightTriangle,self.SubErrorMarker);
    self._editor.markerDefine(QextScintilla.RightTriangle,self.CurrentErrorMarker);
    self._editor.setMarkerForegroundColor(QColor("red"),self.ErrorMarker);
    self._editor.setMarkerForegroundColor(QColor("grey"),self.SubErrorMarker);
    self._editor.setMarkerForegroundColor(QColor("red"),self.CurrentErrorMarker);
    self._editor.setMarkerBackgroundColor(QColor("red"),self.CurrentErrorMarker);
    self._editor.setMarginSensitivity(1,True);
    QObject.connect(self._editor,SIGNAL("marginClicked(int,int,Qt::ButtonState)"),self._process_margin_click);
    QObject.connect(self._editor,SIGNAL("textChanged()"),self._text_changed);
    QObject.connect(self._editor,SIGNAL("modificationChanged(bool)"),self._text_modified);
    QObject.connect(self._editor,SIGNAL("cursorPositionChanged(int,int)"),self._display_cursor_position);
    # QObject.connect(self._editor,SIGNAL("textChanged()"),self._clear_transients);

    # add message window
    self._message_box = QFrame(editor_box);
    lo.addWidget(self._message_box);
    self._message_box.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    self._message_box.setFrameStyle(QFrame.Panel+QFrame.Sunken);
    self._message_box.setLineWidth(2);
    mblo = QVBoxLayout(self._message_box);
    msgb1 = QHBox(self._message_box);
    mblo.addWidget(msgb1);
    self._message_icon = QToolButton(msgb1);
    self._message = QLabel(msgb1);
    self._message.setTextFormat(Qt.RichText);
    self._message.setMargin(0);
    self._message.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    # self._message_icon.setAlignment(Qt.AlignTop);
    # self._message_icon.setMargin(4);
    self._message_icon.setAutoRaise(True);
    self._message_icon.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed);
    QObject.connect(self._message_icon,SIGNAL("clicked()"),self.clear_message);
    QToolTip.add(self._message_icon,"Click here to clear the message");
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

  def __del__ (self):
    self.has_focus(False);
    
  def disable_editor (self):
    """Called before disabling the editor, as on some versions of PyQt
    the object is not destroyed properly and keeps receving signals""";
    self._enabled = False;
    
  def show_compile_options (self):
    self._options_menu.show();
    
  def show_runtime_options (self):
    self._jobmenu.show();
    
  def tree_is_in_sync (self,sync=True):
    """Tells the editor wheether the current tree is in sync with the content of the script.
    This is indicated by a visual cue on the toolbar.
    """;
    QToolTip.remove(self._tb_jobs);
    if sync:
      self._tb_jobs.setIconSet(pixmaps.gear.iconset());
      QToolTip.add(self._tb_jobs,"Access run-time options & jobs defined by this TDL script");
    else:
      self._tb_jobs.setIconSet(pixmaps.exclaim_yellow_warning.iconset());
      QToolTip.add(self._tb_jobs,"""Access run-time options & jobs defined by this TDL script.
Warning! You have modified the script since it was last compiled, so the tree may be out of date.""");
  
  def _file_closed (self):
    self.emit(PYSIGNAL("fileClosed()"),(self,));

  def hideEvent (self,ev):
    self.emit(PYSIGNAL("hidden()"),());
    self.emit(PYSIGNAL("visible()"),(False,));
    return QFrame.hideEvent(self,ev);

  def showEvent (self,ev):
    self.emit(PYSIGNAL("shown()"),());
    self.emit(PYSIGNAL("visible()"),(True,));
    return QFrame.showEvent(self,ev);

  def hide_jobs_menu (self,dum=False):
    if self._closed:
      return;
    self._tb_jobs.hide();
    self.clear_message();

  def show_line_numbers (self,show):
    if show:
      self._editor.setMarginWidth(1,36);
    else:
      self._editor.setMarginWidth(1,12);
    self._editor.setMarginLineNumbers(1,show);

  def show_run_control (self,show=True):
    if self._closed:
      return;
    self._tb_run.setShown(show);

  def enable_controls (self,enable=True):
    if self._closed:
      return;
    self._tb_run.setEnabled(enable);
    self._tb_jobs.setEnabled(enable);
    if not enable:
      self.clear_message();

  def disable_controls (self,disable=True):
    if self._closed:
      return;
    self._tb_run.setDisabled(disable);
    self._tb_jobs.setDisabled(disable);
    if disable:
      self.clear_message();

  def get_filename (self):
    return self._filename;
  def get_mainfile (self):
    return self._mainfile;

  def _import_main_file (self):
    # self._tb_opts.setOn(False);
    self.clear_errors();
    if self._mainfile and self._editor.isModified():
      self._save_file();
    self.emit(PYSIGNAL("importFile()"),(self,self._mainfile or self._filename,));

  def _import_as_main_file (self):
    self.clear_errors();
    self._set_mainfile(None);
    self._text_modified(self._editor.isModified());   # to reset labels
    self.emit(PYSIGNAL("fileChanged()"),(self,));
    self.emit(PYSIGNAL("importFile()"),(self,self._filename,));
    
  def _run_main_file (self):
    # self._tb_opts.setOn(False);
    self.clear_errors();
    if self._mainfile and self._editor.isModified():
      self._save_file();
    self.emit(PYSIGNAL("compileFile()"),(self,self._mainfile or self._filename,));

  def _clear_transients (self):
    """if message box contains a transient message, clears it""";
    if self._message_transient:
      self.clear_message();

  def _text_changed (self):
    self._clear_transients();
#    self._qa_run.setVisible(True);

  def _display_cursor_position (self,line,col):
    self._poslabel.setText("L:<b>%d</b> C:<b>%d</b>" % (line+1,col+1));
    self._poslabel.repaint();

  def _text_modified (self,mod):
    self._modified = mod;
    self.emit(PYSIGNAL("textModified()"),(self,bool(mod),));
    if mod:
      self._tb_save.setPaletteBackgroundColor(self._tb_save._modified_color);
    else:
      self._tb_save.unsetPalette();
    if self._filename:
      label = '<b>' + self._basename + '</b>';
      QToolTip.add(self._pathlabel,self._filename);
    else:
      label = '';
      QToolTip.remove(self._pathlabel);
    if self._mainfile:
      label += ' (from <b>' + self._mainfile_base +'</b>)';
    if self._readonly:
      label = '[r/o] ' + label;
    if mod:
      self._clear_transients();
      label = '[mod] ' + label;
    self._pathlabel.setText(label);

  def clear_message (self):
    # print "******* clear_message";
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

  def show_message (self,msg,error=False,iconset=None,transient=False):
    """Shows message in box.
    If iconset is not None, overrides standard icon.
    If error=True, uses error icon (iconset overrides this).
    If transient=True, message will be cleared when text is edited.
    """;
    self._message.setText(msg);
    if not iconset:
      if error:
        iconset = pixmaps.red_round_cross.iconset();
      else:
        iconset = pixmaps.info_blue_round.iconset();
    self._message_icon.setIconSet(iconset);
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

  def _reset_errors (self,nerr):
    """helper method, resets error markers and such. Usually tied to a hasErrors() signal
    from an error window""";
    if not self._enabled:
      return;
    self._editor.markerDeleteAll(self.ErrorMarker);
    self._editor.markerDeleteAll(self.SubErrorMarker);
    self._editor.markerDeleteAll(self.CurrentErrorMarker);
    self._error_at_line = {};
    nerr_local = 0;
    if nerr:
      error_locations = self._error_window.get_error_locations();
      for err_num,filename,line,column,suberror in error_locations:
        if filename == self._filename:
          self._error_at_line[line-1] = err_num;
          if suberror:
            self._editor.markerAdd(line-1,self.SubErrorMarker);
          else:
            self._editor.markerAdd(line-1,self.ErrorMarker);
          nerr_local += 1;
    self.emit(PYSIGNAL("hasErrors()"),(self,nerr_local,));

  def show_error (self,err_num,filename,line,column):
    """Shows error at the given position, but only if the filename matches.
    Can be directly connected to a showError() signal from an error window""";
    self._editor.markerDeleteAll(self.CurrentErrorMarker);
    if filename == self._filename:
      # scintilla's line numbers are 0-based
      self._editor.ensureLineVisible(line-1);
      self._editor.setCursorPosition(line-1,column);
      # a little kludge to prevent line from being hidden by a resize
      self._editor.ensureLineVisible(line+4);
      self._editor.markerAdd(line-1,self.CurrentErrorMarker);

  def _process_margin_click (self,margin,line,button):
    _dprint(1,margin,line,button);
    # look through current error widget to find relevant error
    err_num = self._error_at_line.get(line,None);
    if err_num is not None:
      self._error_window.show_error_number(err_num);

  def sync_external_file (self,filename=None,ask=True):
    #
    # NB: problem because it resets the errors
    filename = filename or self._filename;
    filetime = _file_mod_time(filename);
    if not filetime or filetime == self._file_disktime:
      return True;  # in sync
    if not ask:
      res = 1;
    else:
      res = QMessageBox.warning(self,"TDL file changed",
        """<p><tt>%s</tt> has been modified by another program.
        Would you like to overwrite the disk version, revert to the disk
        version, or cancel the operation?"""
        % (filename,),
        "Overwrite","Revert","Cancel",-1,2);
    if res == 2:
      return None;
    elif res == 1:
      if filename != self._filename:
        self.load_file(filename);
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
      try: dialog = self._save_as_dialog;
      except AttributeError:
        self._save_as_dialog = dialog = QFileDialog(self,"save tdl dialog",True);
        dialog.resize(800,dialog.height());
        dialog.setMode(QFileDialog.AnyFile);
        dialog.setFilters("TDL scripts (*.tdl);;Python scripts (*.py);;All files (*.*)");
        dialog.setViewMode(QFileDialog.Detail);
        dialog.setCaption("Save TDL Script");
      else:
        dialog.rereadDir();
      if dialog.exec_loop() != QDialog.Accepted:
        return None;
      filename = str(dialog.selectedFile());
    # save the file
    if text is None:
      text = str(self._editor.text());
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
    self._editor.setModified(False);
    self._text_modified(False);
    self.emit(PYSIGNAL("fileSaved()"),(self,filename,));
    return self._filename;

  def close (self):
    self._closed = True;

  def confirm_close (self):
    if self._modified:
      res = QMessageBox.warning(self,"TDL file modified",
        """Save modified file <p><tt>%s</tt>?</p>"""
        % (self._filename or "",),
        "Save","Don't Save","Cancel",0,2);
      if res == 2:
        return False;
      if res == 0:
        if not self._save_file():
          return False;
    self.close();
    return True;

  def _revert_to_saved (self,force=False):
    if not self._filename:
      return;
    if not force:
      if QMessageBox.question(self,"Revert to saved",
        """Revert to saved version of <p><tt>%s</tt>?"""
        % (self._filename,),
        "Revert","Cancel","",0,1):
        return;
    self.load_file(self._filename);

  def _add_menu_label (self,menu,label):
    tlab = QLabel("<b>"+label+"</b>",menu);
    tlab.setAlignment(Qt.AlignCenter);
    tlab.setFrameShape(QFrame.ToolBarPanel);
    tlab.setFrameShadow(QFrame.Sunken);
    menu.insertItem(tlab);
    
  def has_compile_options (self):
    return self._options_menu.listView().childCount();
  
  def has_runtime_options (self):
    return self._jobmenu.listView().childCount();

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
    _dprint(1,self._filename,"importing");
    self.clear_message();
    self.clear_errors();
    # change the current directory to where the file is
    # os.chdir(os.path.dirname(self._filename));
    # The Python imp module expects text to reside in a disk file, which is
    # a pain in the ass for us if we're dealing with modified text or text
    # entered on-the-fly. So, either save or sync before proceeding
    global _external_sync;
    if self._editor.isModified() or not self._filename:
      if not self._save_file():
        return None;
    else:
      if not self.sync_external_file(ask=False):
        return None;
    # if we already have an imported module and disk file hasn't changed, skip
    #the importing step
    if force or self._tdlmod is None or self._tdlmod_filetime == self._file_disktime:
      # reset data members
      _dprint(2,self._filename,"emitting signal for 0 compile-time options");
      self.emit(PYSIGNAL("hasCompileOptions()"),(self,0,));
      self._options_menu.hide();
      self._options_menu.clear();
      self._tdlmod = None;
      # get text from editor
      tdltext = str(self._editor.text());
      try:
        tdlmod,tdltext = TDL.Compile.import_tdl_module(self._filename,tdltext);
      # catch import errors
      except TDL.CumulativeError as value:
        _dprint(0,"caught cumulative error, length",len(value.args));
        self._error_window.set_errors(value.args,message="TDL import failed");
        return None;
      except Exception as value:
        _dprint(0,"caught other error, traceback follows");
        traceback.print_exc();
        self._error_window.set_errors([value],message="TDL import failed");
        return None;
      # remember module and nodescope
      self._tdlmod = tdlmod;
      self._tdltext = tdltext;
      self._tdlmod_filetime = self._file_disktime;
      # build options menu from compile-time options
      opt_listview = self._options_menu.listView();
      opts = TDLOptions.get_compile_options();
      if opts:
        # add options
        try:
          TDLOptions.populate_option_treewidget(opt_listview,opts);
        except Exception as value:
          _dprint(0,"error setting up TDL options GUI");
          traceback.print_exc();
          self._error_window.set_errors([value],message="Error setting up TDL options GUI");
          return None;
        # self._tb_opts.show();
        _dprint(2,self._filename,"emitting signal for",len(opts),"compile-time options");
        self.emit(PYSIGNAL("hasCompileOptions()"),(self,len(opts),));
    # success, show options or compile
    if show_options and self.has_compile_options():
      self._options_menu.show();
    return True;
      
  def compile_content (self):
    # import content first, and return if failed
    if not self.import_content(force=True):
      return None;
    _dprint(1,self._filename,"compiling forest");
    # clear predefined functions
    self._tb_jobs.hide();
    # make list of publishing nodes
    pub_nodes = [ node.name for node in meqds.nodelist.iternodes()
                  if node.is_publishing() ];
    # try the compilation
    try:
      QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
      try:
        (_tdlmod,ns,msg) = \
          TDL.Compile.run_forest_definition(
              meqds.mqs(),self._filename,self._tdlmod,self._tdltext,
              parent=self,wait=False);
      finally:
        QApplication.restoreOverrideCursor();
    # catch compilation errors
    except TDL.CumulativeError as value:
      _dprint(0,"caught cumulative error, length",len(value.args));
      self._error_window.set_errors(value.args,message="TDL import failed");
      return None;
    except Exception as value:
      _dprint(0,"caught other error, traceback follows");
      traceback.print_exc();
      self._error_window.set_errors([value]);
      return None;
    # refresh the nodelist
    meqds.request_nodelist(sync=True);
    # restore publishing nodes
    for name in pub_nodes:
      if name in ns.AllNodes():
        meqds.enable_node_publish_by_name(name,sync=True);
    ### NB: presume this all was successful for now
    # insert node scope into TDL module
    setattr(_tdlmod,'_tdl_nodescope',ns);

    # does the script define an explicit job list?
    joblist = getattr(_tdlmod,'_tdl_job_list',[]);
    if not joblist:
      joblist = [];
      # try to build it from implicit function names
      for (name,func) in _tdlmod.__dict__.items():
        if name.startswith("_tdl_job_") and callable(func):
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
    joblist.sort(key=cmp_to_key(lambda a,b:cmp(str(a),str(b))));

    # create list of job actions
    opts = TDLOptions.get_runtime_options();
    self._jobmenu.clear();
    if joblist or opts:
      self._tb_jobs.setOn(False);
      self._tb_jobs.show();
      if opts:
        self._job_executor = curry(self.execute_tdl_job,_tdlmod,ns);
        ## new style:
        try:
          TDLOptions.populate_option_treewidget(self._jobmenu.listView(),opts,executor=self._job_executor);
        except Exception as value:
          _dprint(0,"error setting up TDL options GUI");
          traceback.print_exc();
          self._error_window.set_errors([value],message="Error setting up TDL options GUI");
          return None;
      if joblist:
        for func in joblist:
          name = re.sub("^_tdl_job_","",func.__name__);
          name = name.replace('_',' ');
          self._jobmenu.addAction(name,
              curry(self.execute_tdl_job,_tdlmod,ns,func,name),
              icon=pixmaps.gear);
      self.emit(PYSIGNAL("hasRuntimeOptions()"),(self,True));
    else:
      self.emit(PYSIGNAL("hasRuntimeOptions()"),(self,False));
      self._tb_jobs.hide();

    if joblist:
      msg += " %d predefined function(s) available, please use the Exec menu to run them." % (len(joblist),);

    self.show_message(msg,transient=True);
    return True;

  def execute_tdl_job (self,_tdlmod,ns,func,name):
    """executes a predefined TDL job given by func""";
    self._jobmenu.hide();
    try:
      # log job 
      TDLOptions.dump_log("running TDL job '%s'"%name);
      QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
      try:
        func(meqds.mqs(),self);
      finally:
        QApplication.restoreOverrideCursor();
      # no errors, so clear error list, if any
      self.clear_errors();
      self.show_message("TDL job '"+name+"' executed.",transient=True);
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
      self._error_window.set_errors(ns.GetErrors(),signal=True,message=msg);
      self.emit(PYSIGNAL("showEditor()"),(self,));

  def get_jobs_popup (self):
    return self._jobmenu;

  def get_options_popup (self):
    return self._options_menu;

  def _set_mainfile (self,mainfile):
    """adjusts GUI controls based on whether we are a mainfile or not""";
    self._mainfile = mainfile;
    self._mainfile_base = mainfile and os.path.basename(mainfile);
    # if we have a mainfile, add extra options for the Run button
    if mainfile:
      self._tb_run.setPopup(self._tb_runmenu);
      QToolTip.add(self._tb_run,"Saves this script and runs the main script "+self._mainfile_base+". Click on the down-arrow for other options.");
      self._qa_runmain.setToolTip("Saves this script and runs the main script "+self._mainfile_base+".");
      self._qa_runmain.setMenuText("Run "+self._mainfile_base);
    else:
      self._tb_run.setPopup(None);
      QToolTip.add(self._tb_run,"Saves and runs the script.");
      
  def reload_file (self):
    text = open(self._filename).read();
    # set save icons, etc.
    self._qa_revert.setEnabled(True);
    self._file_disktime = _file_mod_time(self._filename);
    self._editor.setText(text);
    self._editor.setReadOnly(not os.access(self._filename,os.W_OK));
    self._editor.setModified(False);
    self._text_modified(False);

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
    self._editor.setText(text);
    self._editor.setReadOnly(readonly);
    self._editor.setModified(False);
    self._text_modified(False);
    # emit signals
    self.emit(PYSIGNAL("fileLoaded()"),(self,filename,));
    # if module is a main-level file (i.e. not slaved to another mainfile),
    # pre-import it so that compile-time menus become available
    self._tdlmod = None;
    if not mainfile:
      self.import_content();

  def adjust_editor_font (self):
    self._editor.setFont(self.font());
    self._lexer.setDefaultFont(self.font());
    self._lexer.setFont(self.font(),-1);
    ps = self.fontInfo().pointSize()+self._editor_fontadjust;
    self._editor.zoomTo(ps);

  def has_focus (self,focus):
    if focus:
      TDLEditor.current_editor = self;
    else:
      if TDLEditor.current_editor == self:
        TDLEditor.current_editor = None;


class TDLOptionsDialog (QDialog,PersistentCurrier):
  """implements a floating window for TDL options""";
  def __init__ (self,parent,ok_label=None,ok_icon=None):
    QDialog.__init__(self,parent,"options",False);
    self.setSizeGripEnabled(True);
    
    lo_main = QVBoxLayout(self,11,6);
    # add option listview
    self._listview = listview = QListView(self);
    listview.addColumn("");
    listview.addColumn("");
    listview.addColumn("");
    listview.setRootIsDecorated(True);
    listview.setShowToolTips(True);
    listview.setSorting(-1);
    listview.setResizeMode(QListView.LastColumn);
    # listview.header().hide();
    # listview.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    # add signals
    QObject.connect(listview,SIGNAL("clicked(QListViewItem*)"),self._process_listview_click);
    QObject.connect(listview,SIGNAL("pressed(QListViewItem*)"),self._process_listview_press);
    QObject.connect(listview,SIGNAL("returnPressed(QListViewItem*)"),self._process_listview_click);
    QObject.connect(listview,SIGNAL("spacePressed(QListViewItem*)"),self._process_listview_click);
    QObject.connect(listview,SIGNAL("doubleClicked(QListViewItem*,const QPoint &, int)"),
                            self._process_listview_click);
    # listview.setMinimumSize(QSize(200,100));
    lo_main.addWidget(listview);
    # set geometry
    # self.setMinimumSize(QSize(200,100));
    # self.setGeometry(0,0,200,60);
    
    # add buttons on bottom
    lo_btn  = QHBoxLayout(None,0,6);
    if ok_label:
      if ok_icon:
        tb = QPushButton(ok_icon.iconset(),ok_label,self);
      else:
        tb = QPushButton(ok_label,self);
      lo_btn.addWidget(tb);
      QObject.connect(tb,SIGNAL("clicked()"),self.accept);
    # add cancel button
    tb = QPushButton(pixmaps.red_round_cross.iconset(),"Cancel",self);
    QObject.connect(tb,SIGNAL("clicked()"),self.hide);
    spacer = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum);
    lo_btn.addItem(spacer)
    lo_btn.addWidget(tb);
    lo_main.addLayout(lo_btn);
    self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
    
  def accept (self):
    self.emit(PYSIGNAL("accepted()"),());
    self.hide();
    
  def show (self):
    self._listview.adjustColumn(0);
    self._listview.adjustColumn(1);
    return QDialog.show(self);
  
  def exec_loop (self):
    self._listview.adjustColumn(0);
    self._listview.adjustColumn(1);
    return QDialog.exec_loop(self);
  
  def listView (self):
    return self._listview;
  
  def clear (self):
    self._listview.clear();
    
  class ActionListViewItem (QListViewItem):
    def paintCell (self,qp,cg,column,width,align):
      # use bold font for jobs
      oldfont = qp.font();
      font = QFont(oldfont);
      font.setBold(True);
      qp.setFont(font);
      QListViewItem.paintCell(self,qp,cg,column,width,align);
      qp.setFont(oldfont);
    def width (self,fm,lv,c):
      return int(QListViewItem.width(self,fm,lv,c)*1.2);
    
  def addAction (self,label,callback,icon=None):
    # find last item
    last = self._listview.firstChild();
    while last and last.nextSibling():
      last = last.nextSibling();
    item = self.ActionListViewItem(self._listview,last);
    item.setText(0,label);
    if icon:
      item.setPixmap(0,icon.pm());
    item._on_click = callback;
    item._close_on_click = True;
    self._listview.adjustColumn(0);
    self._listview.adjustColumn(1);
    
  def _process_listview_click (self,item,*dum):
    """helper function to process a click on a listview item. Meant to be connected
    to the clicked() signal of a QListView""";
    on_click = getattr(item,'_on_click',None);
    if on_click:
      on_click();
    if getattr(item,'_close_on_click',False):
      self.hide();
      
  def _process_listview_press (self,item,*dum):
    """helper function to process a press on a listview item. Meant to be connected
    to the pressed() signal of a QListView""";
    on_click = getattr(item,'_on_press',None);
    if on_click:
      on_click();

class TDLErrorFloat (QMainWindow,PersistentCurrier):
  """implements a floating window for TDL error reports""";
  def __init__ (self,parent):
    fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
    fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title;
    QMainWindow.__init__(self,parent,"float",fl);
    self.hide();
    self.setIcon(pixmaps.red_round_cross.pm());
    self.setCaption("TDL Errors");
    # make widgets
    self._werrlist_box = QVBox(self);
    self.setCentralWidget(self._werrlist_box);
    # error list header is a toolbar
    errlist_hdr = QToolBar("TDL errors",self,self._werrlist_box);
    errlist_hdr.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed);
    # prev/next error buttons
    self._qa_prev_err = QAction(pixmaps.red_leftarrow.iconset(),"Show &previous error",Qt.ALT+Qt.Key_P,self);
    self._qa_prev_err.addTo(errlist_hdr);
    QObject.connect(self._qa_prev_err,SIGNAL("activated()"),self._show_prev_error);
    self._qa_next_err = QAction(pixmaps.red_rightarrow.iconset(),"Show &next error",Qt.ALT+Qt.Key_N,self);
    self._qa_next_err.addTo(errlist_hdr);
    QObject.connect(self._qa_next_err,SIGNAL("activated()"),self._show_next_error);
    # label with error count
    self._error_count_label = QLabel(errlist_hdr);
    errlist_hdr.setStretchableWidget(self._error_count_label);
    self._error_count_label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed);
    # error list itself
    self._werrlist = QListView(self._werrlist_box);
    self._werrlist.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred);
    QObject.connect(self._werrlist,SIGNAL("currentChanged(QListViewItem*)"),self.curry(self._process_item_click,"currentChanged"));
    QObject.connect(self._werrlist,SIGNAL("clicked(QListViewItem*)"),self.curry(self._process_item_click,"clicked"));
    QObject.connect(self._werrlist,SIGNAL("spacePressed(QListViewItem*)"),self.curry(self._process_item_click,"spacePressed"));
    QObject.connect(self._werrlist,SIGNAL("returnPressed(QListViewItem*)"),self.curry(self._process_item_click,"returnPressed"));
    QObject.connect(self._werrlist,SIGNAL("expanded(QListViewItem*)"),self.curry(self._process_item_click,"expanded"));
    self._werrlist.addColumn('');
    self._werrlist.addColumn('');
    self._werrlist.addColumn('');
    self._werrlist.addColumn('');
    self._werrlist.setSorting(-1);
    self._werrlist.setRootIsDecorated(True);
    self._werrlist.setAllColumnsShowFocus(True);
    self._werrlist.header().hide();
    # size the widget
    self.setMinimumSize(QSize(200,60));
    self.setGeometry(0,0,200,60);
    # anchor and position relative to anchor
    self._anchor_widget = None;
    self._anchor_xy0 = None;
    self._anchor_xy  = 0,0;
    self._current_xy = 0,0;
    self._anchor_ref = 0,0;
    self._anchoring = False;
    # explicit geometry set via anchor, None of none set
    self._geom = None;
    # timer used for move operations
    self._move_timer = QTimer(self);
    # internal state
    self._item_shown = None;
    self._in_show_error_item = False;
    self._error_list = [];

  def closeEvent (self,ev):
    """Window closed: hide and set a flag""";
    self.hide();
    ev.ignore();

  def show (self):
    """Only show the window if we have errors in it""";
    if self._error_list:
      QMainWindow.show(self);

  def moveEvent (self,ev):
    QMainWindow.moveEvent(self,ev);
#    print "moveEvent spontaneous:",ev.spontaneous();
    # ignore move events for some time after a move_anchor() -- these are probably caused
    # by the anchor moving us, and not by the user
    if not self._move_timer.isActive():
      self._current_xy = self.geometry().x(),self.geometry().y();
#      print "current xy is",self._current_xy;

  def showEvent (self,ev):
#    print "showEvent spontaneous:",ev.spontaneous();
    if not ev.spontaneous():
      x,y = self._current_xy;
      self.setGeometry(x,y,self.width(),self.height());
      self._move_timer.start(200,True);
    QMainWindow.showEvent(self,ev);
#    print "showEvent ends";

  def set_anchor (self,widget,x,y,xref=0,yref=0):
    """Tells the window to anchor itself to point x,y of the given widget.
    If xref is 0, x is relative to the left side, otherwise to the right side.
    If yref is 0, y is relative to the top edge, otherwise to the bottom edge.
    """;
    self._anchor_widget = widget;
    self._anchor_xy = x,y;
    self._anchor_ref = xref,yref;
#    print "anchoring to",x,y,xref,yref;
    self.move_anchor();

  def move_anchor (self):
    """Notifies the window that its anchor widget has moved around.
    Changes position following the anchor.""";
    # get dx,dy coordinates relative to old anchor point
    if self._anchor_xy0 is not None:
      x0,y0 = self._anchor_xy0;
      x,y = self._current_xy;
#      print "move_anchor: old location is",x,y;
      dx = x - x0;
      dy = y - y0;
    else:
      dx = dy = 0;
#    print "move_anchor: dxy relative to old anchor is",dx,dy;
    # compute new anchoring point
    top = self._anchor_widget.mapToGlobal(QPoint(0,0));
    btm = self._anchor_widget.mapToGlobal(QPoint(self._anchor_widget.width(),
                          self._anchor_widget.height()));
    #print "move_anchor: widget top is",top.x(),top.y();
    #print "move_anchor: widget btm is",btm.x(),btm.y();
    x,y = self._anchor_xy;
    # add to coordinates of reference point on anchor
    if self._anchor_ref[0]:
      x0 = btm.x() + x;
    else:
      x0 = top.x() + x;
    if self._anchor_ref[1]:
      y0 = btm.y() + y;
    else:
      y0 = top.y() + y;
    # move to new location
    #print "move_anchor: new location is",x0,y0;
    self._anchor_xy0 = x0,y0;
    self._current_xy = x0+dx,y0+dy;
    self.setGeometry(x0+dx,y0+dy,self.width(),self.height());
    # Start a timer to ignore move events for a bit. The reason for this is that sometimes
    # very rapid moving of the main window causes the float to "lag" because the setGeometry()
    # call is not processed before another call to move_anchor(). A small delay should eliminate this.
    self._move_timer.start(200,True);

  def _populate_error_list (self,parent,errlist,toplevel=False):
    """helper function to recursively populate the error ListView""";
    previtem = None;
    for index,err in enumerate(errlist):
      if isinstance(err,TDL.TDLError):
        errmsg = str(err.args[0]);
      else:
        errmsg = str(err);
      filename = getattr(err,'filename',None);
      line = getattr(err,'lineno',0);
      column = getattr(err,'offset',0) or 0;  # offset is sometimes None, make sure this is 0
      suberror = isinstance(err,TDL.NestedTDLError);
      _dprint(1,errmsg,"at",filename,line,column);
      # index of corresponding top-level item
      toplevel_index = len(self._toplevel_error_items)-1;
      if toplevel:
        toplevel_index += 1;
      # create item
      if previtem is not None:
        previtem = item = QListViewItem(parent,previtem,"%d:"%(toplevel_index+1,));
      else:
        previtem = item = QListViewItem(parent,"%d:"%(toplevel_index+1,));
      # add housekeeping info
      item._toplevel_index = toplevel_index;
      if toplevel:
        self._toplevel_error_items.append(item);
      toplevel_index = len(self._toplevel_error_items)-1;
      self._error_items.append(item);
      item.setOpen(False);
      # set item content
      if filename is None:
        item.setText(1,errmsg);
        item.setText(2,"<unknown>");
        item.setText(3,"(%s)"%err.__class__.__name__);
      else:
        # normalize filenames: eliminate CWD, leave just one path element
        fname = filename;
        try: is_cwd = os.path.samefile(os.path.dirname(fname),'.');
        except: is_cwd = False;
        if is_cwd:
          fname = os.path.basename(filename);
        else:
          dirname,fname = os.path.split(filename);
          dir1,dir2 = os.path.split(dirname);
          if dir1 == '/' or not dir1:
            fname = filename;
          else:
            fname = os.path.join("...",dir2,fname);
        item.setText(1,errmsg);
        item.setText(3,"(%s)"%err.__class__.__name__);
        item._err_location = len(self._error_items)-1,filename,line,column,suberror;
        self._error_locations.append(item._err_location);
        item.setText(2,"[%s:%d]" % (fname,line));
      # recursively populate with nested errors if needed
      nested = getattr(err,'nested_errors',None);
      if nested:
        self._populate_error_list(item,nested);

  def set_errors (self,error_list,signal=True,show_item=True,
                      message="TDL compile failed"):
    """Shows an error list. errlist should be a sequence of Exception
    objects following the TDL error convention.
    message is a status message
    If show_item=True, highlights the first error
    If signal=True, emits a hasErrors(nerr) pysignal
    """;
    _dprint(1,"set_errors: list of",len(error_list),"entries");
    _dprint(1,"current list has",len(self._error_list),"entries");
    # do nothing if already set
    if self._error_list is error_list:
      return;
    self.clear_errors(emit_signal=False);
    self._error_list = error_list;
    self._error_locations = [];         # list of error locations
    self._error_items = [];
    self._toplevel_error_items = [];
    if error_list:
      self._populate_error_list(self._werrlist,error_list,toplevel=True);
      nerr = len(self._toplevel_error_items);
      self._error_count_label.setText('%s: <b>%d</b> errors'%(message,nerr));
      self.setCaption("TDL Errors: %d"%nerr);
      self.show();
      if signal:
        self.emit(PYSIGNAL("hasErrors()"),(nerr,));
      if show_item:
        self._show_error_item(self._toplevel_error_items[0]);
      # resize ourselves according to number of errors
      height = (len(self._error_items)+1)*self._werrlist.fontMetrics().lineSpacing();
      height = min(200,height);
      self.setGeometry(self.x(),self.y(),self.width(),height);
      self.updateGeometry();
      # self._highlight_error(0);
      # disable run control until something gets modified
      # self._qa_run.setVisible(False);
    else:
      self.setCaption("TDL Errors");
      self.hide();

  def get_error_list (self):
    return self._error_list;

  def get_error_locations (self):
    return self._error_locations;

  def clear_errors (self,signal=True):
    """clears the error list. If signal=True, emits a hasErrors(0) pysignal""";
    if signal:
      self.emit(PYSIGNAL("hasErrors()"),(0,));
    self._error_items = self._toplevel_error_items = None;
    self.setCaption("TDL Errors");
    self._werrlist.clear();
    self._error_count_label.setText('');
    self._error_list = [];
    self._error_locations = [];
    self._item_shown = None;
    self.hide();

  def _highlight_error_item (self,item,signal=True):
    """highlights the given error item. If signal=True, emits a
    showError(index,filename,line,column) or showError(None) pysignal.
    """;
    if item:
      self.show();
      toplevel_index = item._toplevel_index;
      self._qa_prev_err.setEnabled(toplevel_index > 0);
      self._qa_next_err.setEnabled(toplevel_index < len(self._toplevel_error_items)-1);
      # does item contain a location attribute?
      errloc = getattr(item,'_err_location',None);
      if errloc:
        # indicate location
        _dprint(1,"highlighting error in",errloc);
        if signal:
          self.emit(PYSIGNAL("showError()"),errloc);
        return
    # if we fell through to here, then no error has been shown -- emit appropriate signal
    if signal:
      self.emit(PYSIGNAL("showError()"),(None,None,None,None));

  def _show_next_error (self):
    item = self._werrlist.currentItem();
    if item:
      toplevel_index = item._toplevel_index + 1;
      if toplevel_index >= len(self._toplevel_error_items):
        toplevel_index = 0;
      item = self._toplevel_error_items[toplevel_index];
    else:
      item = self._error_items[0];
    if item:
      self._show_error_item(item);

  def _show_prev_error (self):
    item = self._werrlist.currentItem();
    if item:
      toplevel_index = item._toplevel_index - 1;
      if toplevel_index < 0:
        toplevel_index = len(self._toplevel_error_items)-1;
      item = self._toplevel_error_items[toplevel_index];
    else:
      item = self._toplevel_error_items[-1];
    if item:
      self._show_error_item(item);

  def show_error_number (self,index,signal=True):
    self._show_error_item(self._error_items[index],signal=signal);

  def _show_error_item (self,item,signal=True):
    # do nothing if item is None, or already shown, or if already within this function
    if item is None or self._in_show_error_item or item is self._item_shown:
      return;
    self._in_show_error_item = True;
    try:
      self._item_shown = item;
      self._werrlist.setCurrentItem(item);
      self._werrlist.setSelected(item,True);
      for other in self._toplevel_error_items:
        if other is item:
          other.setOpen(True);
        else:
          other.setOpen(False);
      self._werrlist.ensureItemVisible(item);
      self._highlight_error_item(item,signal=signal);
    finally:
      self._in_show_error_item = False;

  def _process_item_click (self,why,item):
    self._show_error_item(item,signal=True);


class TDLFileDataItem (Grid.DataItem):
  """represents a GridDataItem for a TDL script""";
  def __init__ (self,pathname):
    # read the file (exception propagated outwards on error)
    ff = open(pathname);
    text = ff.read();
    ff.close();
    basename = os.path.basename(pathname);
    # create the item
    udi = '/tdlfile/'+pathname;
    name = basename;
    caption = '<b>'+basename+'</b>';
    desc = 'TDL file '+pathname;
    Grid.DataItem.__init__(self,udi,name=name,caption=caption,desc=desc,data=text,viewer=TDLBrowser,refresh=None);
    # add extra pathname attribute for tdl objects
    self.tdl_pathname = pathname;


class TDLBrowser(browsers.GriddedPlugin):
  _icon = pixmaps.text_tdl;
  viewer_name = "TDL Browser";

  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    self._wedit = TDLEditor(self.wparent());
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    if dataitem.data is not None:
      self.set_data(dataitem);
    QObject.connect(self.wtop(),PYSIGNAL("fontChanged()"),self.wtop().adjust_editor_font);

  def wtop (self):
    return self._wedit;
  def editor (self):
    return self._wedit;

  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    pathname = getattr(dataitem,'tdl_pathname',None);
    self._wedit.load_file(pathname,text=dataitem.data);

  def highlight (self,color=True):
    browsers.GriddedPlugin.highlight(self,color);
    self._wedit.has_focus(bool(color));

Grid.Services.registerViewer(str,TDLBrowser,priority=10,check_udi=lambda x:x.endswith('_tdl'));

# # standard method to register actions in the main menu
# #
# def define_mainmenu_actions (menu,parent):
#   _dprint(1,'defining stream control menu actions');
#   global _qa_next,_qa_prev,_qa_run;
#   _qa_next = QAction(pixmaps.blue_round_rightarrow.iconset(),"&Next error",Qt.CTRL+Qt.Key_N,parent);
#   _qa_next.addTo(menu['TDL']);
#   _qa_next.setEnabled(False);
#   _qa_prev = QAction(pixmaps.blue_round_leftarrow.iconset(),"&Previous error",Qt.CTRL+Qt.Key_P,parent);
#   _qa_prev.addTo(menu['TDL']);
#   _qa_prev.setEnabled(False);
#   _qa_run = QAction(pixmaps.blue_round_reload.iconset(),"&Run script",Qt.CTRL+Qt.Key_R,parent);
#   _qa_run.addTo(menu['TDL']);
#   _qa_run.setEnabled(False);
#
