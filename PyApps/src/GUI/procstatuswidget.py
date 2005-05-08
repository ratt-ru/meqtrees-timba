#!/usr/bin/python

from qt import *

class ProcStatusWidget (QLabel):
  
  def __init__(self,parent,width=None,height=None):
    QLabel.__init__(self,parent);
    # self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred));
    if width is not None:
      self.setMinimumWidth(width);
    if height is not None:
      self.setMinimumHeight(height);
    self.setAlignment(Qt.AlignRight);
    # init status
    self._maxsizes = [0,0,0];
    
  def reset (self):
    self._maxsizes = [0,0,0];
  
  def setStatus (self,stat):
    (vsz,rss,shm,code,lib,data,dirty,cpu_sec,cpu_usec) = self._stat = stat;
    lbls = ("VSZ","RSS","DS");
    s = "<nobr><small>";
    # form memory size strings
    for (i,val) in enumerate((vsz,rss,data)):
      val /= 1024;
      self._maxsizes[i] = max(val,self._maxsizes[i]);
      if self._maxsizes[i] != val:
        s += "%s:<b>%d</b>/%dM " % (lbls[i],val,self._maxsizes[i]);
      else:
        s += "%s:<b>%d</b>M " % (lbls[i],val);
    # form cpu time string
    h = cpu_sec/3600;
    cpu_sec %= 3600;
    m = cpu_sec/60;
    cpu_sec %= 60;
    cpu_sec += 0.01*(cpu_usec/10000);
    if h and m:
      s += "cpu:<b>%d:%02d:%.2f</b>"%(h,m,cpu_sec);
    elif m:
      s += "cpu:<b>%d:%.2f</b>"%(m,cpu_sec);
    else:
      s += "cpu:<b>%.2f</b>"%(cpu_sec,);
    # set label
    s += " </small></nobr>";
    self.setText(s);
