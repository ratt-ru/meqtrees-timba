# -*- coding: utf-8 -*-
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

import time

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

from Timba import dmi
from Timba.utils import PersistentCurrier

def hms_str (tm):
  """helper method, converts time in seconds to H:MM:SS string""";
  (tm,secs) = divmod(int(tm),60);
  (tm,mins) = divmod(tm,60);
  return "%d:%02d:%02d"%(tm,mins,secs);

class VisProgressMeter (QWidget):
  """VisProgressMeter implements a one-line progress meter
  to track progress messages from a VisDataMux. It is normally meant
  to be part of a status bar
  """;
  def __init__ (self,parent):
    QWidget.__init__(self,parent);
    lo = QHBoxLayout(self);
    lo.setContentsMargins(5,0,5,0);
    lo.setSpacing(5);
    self._wtime = QLabel(self);
    self._wtime.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum);
    self._wtime.setAlignment(Qt.AlignLeft|Qt.AlignVCenter);
    self._wtime.setIndent(5);
    self._wtime.setTextFormat(Qt.RichText);
    self._wprog = QProgressBar(self);
    self._wprog.setTextVisible(True);
    self._wprog.setMinimumWidth(128);
    self._wprog.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum);
    self._wlabel = QLabel(self);
    self._wlabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    self._wlabel.setIndent(5);
    self._wlabel.setTextFormat(Qt.RichText);
    self._wlabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter);
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    for w in (self._wtime,self._wprog,self._wlabel):
      lo.addWidget(w);
    self._app = None;
    self._vis_output = False;
    self._vis_inittime = None;
    self._timerid = None;
    self._currier = PersistentCurrier();
    self.curry = self._currier.curry;
    self.xcurry = self._currier.xcurry;
    self._timer_id = None;
    self._reset_stats();
    
  class TSStats (object):
    """helper class to contain secs/timeslot stats""";
    def __init__ (self):
      self.reset(None,0);
    def reset (self,tm,nt=None):
      """resets to time0, and optionally a number of timeslots""";
      self.time0 = tm;
      self.nt = nt or 0;
      self.rate = None;
    def mark (self,tm):
      """marks current time and computes rate""";
      if self.nt and self.time0 is not None:
        self.rate = (tm-self.time0)/self.nt;
      return self.rate;
    def update (self,nt):
      """adds number of timeslots""";
      self.nt += nt;
  
  def _reset_stats (self):
    self._stats = self.TSStats();  # total stats
    self._pstats = self.TSStats(); # previous tile's stats
    self._vis_nt = self._vis_rtime0 = self._vis_rtime1 = None;
    self._time_reset_needed = True;  # if true, total time counter will be reset
    self._hdr_time = self._etc_time = None;
    
  def connect_app_signals (self,app):
    """connects standard app signals to appropriate methods."""
    self._app = app;
    QObject.connect(app,PYSIGNAL("vis.channel.open"),self.xcurry(self.start,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.header"),self.xcurry(self.header,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.num.tiles"),self.xcurry(self.update,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.footer"),self.xcurry(self.footer,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("vis.channel.closed"),self.xcurry(self.close,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("isConnected()"),self.xcurry(self.reset));
    
  def _show (self):
    self._wlabel.show();
    self._wprog.show();
    self._wtime.show();
    self.show();
  
  def start (self,rec):
    """initializes and shows meter. Usually connected to a Vis.Channel.Open signal""";
    self._app.statusbar.clearMessage();
    self._wlabel.setText("<nobr>opening dataset</nobr>"); 
    self._wprog.reset();
    self._vis_output = rec.get("output");
    self._vis_inittime = time.time();
    self._wtime.setText(" 0:00:00");
    self._wtime.show();
    self._show();
    if self._timer_id is not None:
      self.killTimer(self._timer_id);
    self._timer_id = self.startTimer(1000);
    self._reset_stats();
    
  def timerEvent (self,ev):
    """redefined to keep clock display ticking"""
    self._update_time();
  
  def _update_time (self):
    txt = '';
    timestamp = time.time();
    if self._vis_inittime is not None:
      txt = hms_str(timestamp-self._vis_inittime);
      if self._etc_time is not None:
        txt += '<small> ETC </small>' + hms_str(self._etc_time-self._vis_inittime);
    self._wtime.setText("<nobr>"+txt+"</nobr>");
  
  def header (self,rec):
    """processes header record. Usually connected to a Vis.Header signal""";
    self._app.statusbar.clearMessage();
    times = rec.header.time_extent;
    nt = int(times[1] - times[0]);
    self._wprog.setMaximum(nt);
    if nt:
      timestr = "received header, dataset length is " + hms_str(nt);
    else:
      timestr = "received header";
    self._wlabel.setText("<nobr>"+timestr+"</nobr>"); 
    self._reset_stats();
    self._show();
    # init header time
    self._hdr_time = time.time();
       
  def update (self,rec):
    """indicates progress based on a Vis.Num.Tiles signal""";
    timestamp = time.time();
    if self._time_reset_needed:
      self._stats.reset(timestamp);
      self._time_reset_needed = False;
    nt = self._vis_nt = rec.num_tiles;
    ts = rec.timeslots;
    tm0 = rec.time_extent[0];
    nt0 = rec.time_extent[1]-rec.time_extent[0];
    time0 = int(rec.time[0]-tm0);
    time1 = int(rec.time[1]-tm0);
    self._wprog.setMaximum(nt0);
    self._wprog.setValue(time0);
    # compute ETC
    self._etc_time = None;
    if self._hdr_time is not None:
      progress = rec.time[0]-tm0;
      if progress:
        dt = timestamp - self._hdr_time;
        self._etc_time = self._hdr_time + dt*(nt0/progress);
    self._update_time();  
    # compute rates
    nts = ts[1]-ts[0]+1;
    self._stats.mark(timestamp);
    self._pstats.mark(timestamp);
    # form message
    timestr = self._vis_rtime1 = hms_str(time0);
    if self._vis_rtime0 is None:
      self._vis_rtime0 = timestr;
    if time1 != time0:
      timestr1 = self._vis_rtime1 = hms_str(time1);
      timestr += " to " + timestr1;
    msg = " tile <b>%d</b>, t/s %d-%d, r/t %s" \
      % (nt-1,ts[0],ts[1],timestr);
    if self._stats.rate is not None:
      msg = msg+"; avg <b>%.2f</b> sec/ts" % self._stats.rate;
#    if self._pstats.rate is not None:
#      msg = msg+"; last %.2f sec/ts" % self._pstats.rate;
    self._wlabel.setText("<nobr>"+msg+"</nobr>"); 
    # update stat counters
    self._stats.update(nts);
    self._pstats.reset(timestamp,nts);
    # show everything
    self._show();
    
  def footer (self,rec):
    """processes footer record. Usually connected to a Vis.Footer signal""";
    if self._vis_output:
      msg = "received footer, writing to output";
    else:
      msg = "received footer";
    timestamp = time.time();
    self._stats.mark(timestamp);
    self._pstats.mark(timestamp);
    if self._stats.rate is not None:
      msg = msg+"; avg <b>%.2f</b> sec/ts" % self._stats.rate;
    if self._pstats.rate is not None:
      msg = msg+"; last %.2f sec/ts" % self._pstats.rate;
    self._wlabel.setText("<nobr>"+msg+"</nobr>"); 
    self._wprog.setMaximum(100);
    self._wprog.setValue(99);
    self._show();
    
  def close (self,rec):
    """closes meter, posts message describing elapsed time and rate.
    Usually connected to a Vis.Channel.Closed signal.""";
    if self._app:
      msg = "dataset complete";
      rec = dmi.record();
      if self._vis_inittime is not None:
        elapsed = time.time()-self._vis_inittime;
        rec.elapsed = hms_str(elapsed);
        msg += " in "+rec.elapsed;
      else:
        elapsed = None;
      if self._stats.rate is not None:
        rec.secs_per_ts = self._stats.rate;
        msg = msg+"; avg %.2f sec/ts" % rec.secs_per_ts;
      if self._vis_nt is not None:
        rec.num_tiles = self._vis_nt;
        if elapsed is not None:
          rec.secs_per_tile = elapsed/self._vis_nt;
          msg = msg+"; avg %.2f sec/tile" % rec.secs_per_tile;
      if self._vis_rtime0 is not None:
        rec.start_time_rel = self._vis_rtime0;
      if self._vis_rtime1 is not None:
        rec.end_time_rel = self._vis_rtime1;
      self._app.log_message(msg,content=rec);
    self.reset();
    
  def reset (self):
    """resets and hides meter."""
    self._reset_stats();
    if self._timer_id is not None:
      self.killTimer(self._timer_id);
      self._timer_id = None;
    self._vis_inittime = None;
    self._wprog.reset();
    self._wprog.hide();
    self._wlabel.setText(""); 
    self._wlabel.hide();
    self._wtime.setText(""); 
    self._wtime.hide();
    self.hide();
