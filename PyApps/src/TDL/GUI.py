# -*- coding: utf-8 -*-
# Provides GUI services to TDL applications when running under the browser.
# When running in batch mode, most of these map to no-ops

from Timba import dmi
from Kittens.utils import curry

meqbrowser = None;

try:
  from PyQt4 import Qt
except:
  Qt = None;

#
# ===== flush =====
#
if Qt:
  def flush_events ():
    Qt.QCoreApplication.processEvents(Qt.QEventLoop.ExcludeUserInputEvents);
  def _call_gui_func (func,*args):
    ret = func(*args);
    flush_events();
    return ret;
else:
  def flush_events ():
    pass;
  def _call_gui_func (func,*args):
    pass;
    

#
# ===== BUSY INDICATOR =====
#

class BusyIndicator (object):
  """A BusyIndicator object is created to set the cursor to a hourglass.
  When the object is destroyed (i.e. when local variable goes out of scope), the cursor is reset.""";
  def __init__ (self):
    Qt and Qt.QApplication.setOverrideCursor(Qt.QCursor(Qt.Qt.WaitCursor));
  def __del__ (self):
    Qt and Qt.QApplication.restoreOverrideCursor();

#
# ===== PROGRESS DIALOGS =====
#

class ProgressDialog (object):
  def __init__ (self,label,cancel=None,min_duration=0,min_value=0,max_value=100):
    # these methods are directly mapped from QProgressDialog
    methods = [ "setLabelText","setMaximum","setMinimum","setRange","setValue","wasCanceled","show","hide" ];
    if meqbrowser and Qt:
      self.dialog = Qt.QProgressDialog(label,cancel or Qt.QString(),min_value,max_value,meqbrowser);
      self.dialog.setMinimumDuration(min_duration);
      self.dialog.setLabelText(label);
      self.dialog.setValue(min_value);
      self.dialog.show();
      for m in methods:
	      setattr(self,m,curry(_call_gui_func,getattr(self.dialog,m)));
    else:
      self.dialog = None;
      def dummy_method (*arg,**kw):
	      return None;
      for m in methods:
	      setattr(self,m,dummy_method);
  

  def __del__ (self):
    if Qt and self.dialog:
      self.dialog.hide();
      self.dialog.setParent(Qt.QObject());

#
# ===== MESSAGE LOGGING ===
#

# message categories
Normal = 0;
Event  = 1;
Error  = 2;

message_category_names=dict(Normal="normal",Event="event",Error="error");

def log_message (message,category=Normal):
  """Logs a message with the browser, or prints to console.
  Category should be set to Normal, Event or Error."""; 
  if meqbrowser:
    meqbrowser.log_message(message,category=category);
    flush_events();
  else:
    if category == Normal:
      print("TDL message: %s\n"%message);
    else:
      print("TDL %s message: %s"%(message_category_names.get(category,""),message));

#
# ===== MESSAGE BOXES ===
#

# message box types
# when capitalized, these are QMessageBox icon types as well
Critical = 'critical';
Information = 'information';
Question = 'question';
Warning = 'warning';

# copy button types from QMessageBox
Button = dmi.record();
_button_types = ( "Ok","Open","Save","Cancel","Close","Discard","Apply",
                  "Reset","RestoreDefaults","Help","SaveAll","Yes","YesToAll",
                  "No","NoToAll","Abort","Retry","Ignore","NoButton");
ButtonNames = dict();

if Qt:
  for button in _button_types:
    num = getattr(Qt.QMessageBox,button);
    setattr(Button,button,num);
else:
  for i,button in enumerate(_button_types):
    setattr(Button,button,1<<i);

for button in _button_types:
  ButtonNames[getattr(Button,button)] = button;

class MessageBox (object):
  """Implements a persistent message box. Created just like a call to 
   message_box(), and with the same arguments, but also implements
  hide(), show() and setButtonText() methods."""
  def __init__ (self,caption,message,boxtype=Information,buttons=Button.Ok,default=None):
    methods = [ "show","hide","setText" ];
    if meqbrowser and Qt:
      icon = getattr(Qt.QMessageBox,boxtype.capitalize(),Qt.QMessageBox.NoIcon);
      self.dialog = Qt.QMessageBox(icon,caption,message,buttons,meqbrowser);
      if default:
        self.dialog.setDefaultButton(default);
      for m in methods:
        setattr(self,m,curry(_call_gui_func,getattr(self.dialog,m)));
    else:
      self.dialog = None;
      def dummy_method (*arg,**kw):
	      return None;
      for m in methods:
	      setattr(self,m,dummy_method);

  def setBoxType (self,boxtype):
    if self.dialog:
      self.dialog.setIcon(getattr(Qt.QMessageBox,boxtype.capitalize(),Qt.QMessageBox.NoIcon));

  def setButtonText (self,button,text):
    if self.dialog:
      btn = self.dialog.button(button);
      if not btn:
	      raise ValueError("button '%s' not present in this MessageBox"%ButtonNames.get(button,button));
      btn.setText(text);

  def __del__ (self):
    if Qt and self.dialog:
      self.dialog.hide();
      self.dialog.setParent(Qt.QWidget());

def message_box (caption,message,boxtype=Information,buttons=Button.Ok,default=None):
  """Displays a message box.
  'boxtype' is one of Information,Question,Warning or Critical.
  'buttons' is an bitwise-OR of Button entries.
  'default' is default Button.
  """;
  if not meqbrowser or not Qt:
    return default or Button.Ok;
  # print warning if unknown box type
  method = getattr(Qt.QMessageBox,boxtype,None);
  if not method:
    print("WARNING: unknown boxtype '%s' in call to message_box()"%boxtype);
    return default or Button.Ok;
  # call dialog
  Qt.QApplication.setOverrideCursor(Qt.QCursor());
  try:
    result = method(meqbrowser,caption,message,buttons,default);
  finally:
    Qt.QApplication.restoreOverrideCursor();
  return result;

def info_box (caption,message,buttons=Button.Ok,default=Button.Ok):
  return message_box(caption,message,Information,buttons,default);

def warning_box (caption,message,buttons=Button.Ok,default=Button.Ok):
  return message_box(caption,message,Warning,buttons,default);

def error_box (caption,message,buttons=Button.Ok,default=Button.Ok):
  return message_box(caption,message,Critical,buttons,default);

def question_box (caption,message,buttons=Button.Yes|Button.No,default=Button.Yes):
  return message_box(caption,message,Question,buttons,default);

#
# ===== PURR INTERFACE ===
#
      
def purr (dirname,watchdirs=[]):
  """If browser is running, attaches Purr tool to the given directories."""
  if meqbrowser:
    meqbrowser.attach_purr(dirname,watchdirs,modal=False);

