#!/usr/bin/python

from app_browsers import *
from qt import *
from dmitypes import *

class ArrayPlotter(ArrayBrowser,BrowserPlugin):
  _icon = pixmaps.bars3d;
  viewer_name = "Array Plotter";

















gridded_workspace.registerViewer(array_class,ArrayPlotter,priority=-10);
