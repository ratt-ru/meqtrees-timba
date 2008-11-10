#!/usr/bin/python

import sys
import signal
from qt import *

import Purr
import Purr.MainWindow
import Timba.utils

import Purr.Render

# runs Purr standalone
if __name__ == "__main__":
  # parse options is the first thing we should do
  from optparse import OptionParser
  usage = "usage: %prog [options] <directories to watch>"
  parser = OptionParser()
  parser.add_option("-d", "--debug",dest="verbose",type="string",action="append",metavar="Context=Level",
                    help="(for debugging Python code) sets verbosity level of the named Python context. May be used multiple times.");
  parser.add_option("-n", "--no-cwd",dest="no_cwd",action="store_true",
                    help="Do not include '.' in directories to watch.");
  (options, rem_args) = parser.parse_args();
  
  app = QApplication(sys.argv);
  app.setDesktopSettingsAware(True);
  
  # handle SIGINT
  def sigint_handler (sig,stackframe):
    app.quit();
  signal.signal(signal.SIGINT,sigint_handler);
  
  dirnames = list(rem_args);
  if not options.no_cwd and '.' not in dirnames:
    dirnames.append('.');

  purrwin = Purr.MainWindow.MainWindow(None);
  purrwin.attachDirectory(dirnames[0],dirnames);
  purrwin.setPounceMode(purrwin.PounceShow);
  app.setMainWidget(purrwin);
  purrwin.show();
  QObject.connect(app,SIGNAL("lastWindowClosed()"),app,SLOT("quit()"));
  
  app.exec_loop(); 
  print "PURR exiting normally, goodbye!";
