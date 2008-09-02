#!/usr/bin/python
import sys
import os
import os.path

args = sys.argv;
args[0] = 'lwimager';
retcode = os.spawnvp(os.P_WAIT,args[0],args);

if not retcode:
  # find FITS file and run visualizer
  filename = None;
  for arg in args:
    if arg.startswith("fits="):
      filename = arg.split('=')[1];
      break;
  if filename and os.path.exists(filename):
    os.execvp("kvis",["kvis",filename]);