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
    ## disabled for now, since time accounting on 2.6 kernels is broken
    # s += "cpu:" + self.formatTime(cpu_sec,cpu_usec);
    # s += "/" + self.formatTime(cpus_sec,cpus_usec);
    
    s += " </small></nobr>";
    # set label
    self.setText(s);
