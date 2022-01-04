#!/usr/bin/env python3

#
#% $Id$ 
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

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

class ProcStatusWidget (QLabel):
  
  def __init__(self,parent,width=None,height=None):
    QLabel.__init__(self,parent);
    # self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred));
    if width is not None:
      self.setMinimumWidth(width);
    if height is not None:
      self.setMinimumHeight(height);
    self.setIndent(5);
    self.setAlignment(Qt.AlignRight|Qt.AlignVCenter);
    # init status
    self._maxsizes = [0,0,0];
    
  def reset (self):
    self._maxsizes = [0,0,0];
    
  def formatTime(self,sec,usec):
    h = sec/3600;
    sec %= 3600;
    m = sec/60;
    sec %= 60;
    sec += 0.01*(usec/10000);
    if h and m:
      return "<b>%d:%02d:%.2f</b>"%(h,m,sec);
    elif m:
      return "<b>%d:%.2f</b>"%(m,sec);
    else:
      return "<b>%.2f</b>"%(sec,);
  
  def setStatus (self,stat):
    (vsz,rss,shm,code,lib,data,dirty,cpu_sec,cpu_usec,cpus_sec,cpus_usec) = self._stat = stat;
    lbls = ("VSZ","RSS");
    s = "<nobr><small>";
    # form memory size strings
    for (i,val) in enumerate((vsz,rss)):
      val /= 1024;
      self._maxsizes[i] = max(val,self._maxsizes[i]);
      if self._maxsizes[i] != val:
        s += "%s:<b>%d</b>/%dM " % (lbls[i],val,self._maxsizes[i]);
      else:
        s += "%s:<b>%d</b>M " % (lbls[i],val);
    # form cpu time string
    ## disabled for now, since time accounting on 2.6 kernels is broken
    # s += "cpu:" + self.formatTime(cpu_sec,cpu_usec);
    # s += "/" + self.formatTime(cpus_sec,cpus_usec);
    
    s += "</small></nobr>";
    # set label
    self.setText(s);
