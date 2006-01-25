import time
from qt import *

from Timba.utils import PersistentCurrier

def hms_str (tm):
  """helper method, converts time in seconds to H:MM:SS string""";
  (tm,secs) = divmod(int(tm),60);
  (tm,mins) = divmod(tm,60);
  return "%d:%02d:%02d"%(tm,mins,secs);

class VisProgressMeter (QHBox):
  """VisProgressMeter implements a one-line progress meter
  to track progress messages from a VisDataMux. It is normally meant
  to be part of a status bar
  """;
  def __init__ (self,parent):
    QHBox.__init__(self,parent);
    self.setSpacing(5);
    self._wtime = QLabel(self);
    self._wtime.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum);
    self._wprog = QProgressBar(self);
    self._wprog.setCenterIndicator(True);
    self._wprog.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum);
    self._wlabel = QLabel(self);
    self._wlabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    self._app = None;
    self._vis_time0 = 0;
    self._vis_output = False;
    self._vis_inittime = None;
    self._vis_hdrtime = None;
    self._timerid = None;
    self._currier = PersistentCurrier();
    self.curry = self._currier.curry;
    self.xcurry = self._currier.xcurry;
    
  def connect_app_signals (self,app):
    self._app = app;
    QObject.connect(app,PYSIGNAL("vis.channel.open"),self.xcurry(self.start,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.header"),self.xcurry(self.header,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.num.tiles"),self.xcurry(self.update,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.footer"),self.xcurry(self.footer,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.channel.closed"),self.xcurry(self.close,_argslice=slice(1,2)));
  
  def start (self,rec):
    if isinstance(self.parent(),QStatusBar):
      self.parent().clear();
    self._wlabel.setText(" opening dataset "); 
    self._wlabel.show();
    self._wprog.reset();
    self._wprog.show();
    self.show();
    self._vis_output = rec.get("output");
    self._vis_inittime = time.time();
    self._vis_hdrtime = None;
    self._wtime.setText(" 0:00:00");
    self._wtime.show();
    self.killTimers();
    self.startTimer(1000);
    
  def timerEvent (self,ev):
    if self._vis_inittime is not None:
      self._wtime.setText(" "+hms_str(time.time()-self._vis_inittime));
  
  def header (self,rec):
    if isinstance(self.parent(),QStatusBar):
      self.parent().clear();
    times = rec.header.time_extent;
    nt = int(times[1] - times[0]);
    self._vis_time0 = times[0];
    self._wprog.setTotalSteps(nt);
    if nt:
      timestr = " received header, dataset length is " + hms_str(nt)+ " ";
    else:
      timestr = " received header ";
    self._wlabel.setText(timestr); 
    self._wprog.show();
    self.show();
    self._vis_hdrtime = time.time();
       
  def update (self,rec):
    nt = rec.num_tiles;
    ts = rec.timeslots;
    time0 = int(rec.time[0]-self._vis_time0);
    time1 = int(rec.time[1]-self._vis_time0);
    self._wprog.setProgress(time0);
    # compute rate
    if self._vis_hdrtime is not None:
      dt = time.time() - self._vis_hdrtime;
      if ts[0]:
        self._vis_rate = "avg %.2f sec/ts" % (dt/ts[0]);
      else:
        self._vis_rate = None;
    # form message
    timestr = hms_str(time0);
    if time1 != time0:
      timestr += " to " + hms_str(time1);
    msg = " tile %d, timeslots %d to %d, relative time %s" \
      % (nt-1,ts[0],ts[1],timestr);
    if self._vis_rate is not None:
      msg = msg+"; "+self._vis_rate;
    self._wlabel.setText(msg+" "); 
    
  def footer (self,rec):
    if self._vis_output:
      msg = "received footer, writing to output";
    else:
      msg = "received footer";
    if self._vis_rate is not None:
      msg = msg+"; "+self._vis_rate;
    self._wlabel.setText(msg+" "); 
    self._wprog.setProgress(99,100);
    
  def close (self,rec):
    self.killTimers();
    if self._app:
      msg = "dataset complete";
      if self._vis_inittime is not None:
        msg += " in "+hms_str(time.time()-self._vis_inittime);
      if self._vis_rate is not None:
        msg = msg+"; "+self._vis_rate;
      self._app.log_message(msg);
    self._vis_inittime = None;
    self._wlabel.setText(msg+" "); 
    self._wprog.reset();
    self._wprog.hide();
    self._wlabel.setText(""); 
    self._wlabel.hide();
    self._wtime.hide();
    self.hide();
    
