import time
from qt import *

from Timba import dmi
from Timba.utils import PersistentCurrier

class SolverProgressMeter (QHBox):
  """SolverProgressMeter implements a one-line progress meter
  to track progress messages from a Solver. It is normally meant
  to be part of a status bar.
  """;
  def __init__ (self,parent):
    QHBox.__init__(self,parent);
    self.setSpacing(5);
    self._wlabel = QLabel(self);
    self._wlabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    self._wlabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter);
    self._wlabel.setIndent(5);
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    self._app = None;
    self._currier = PersistentCurrier();
    self.curry = self._currier.curry;
    self.xcurry = self._currier.xcurry;
    self._hidetimer = QTimer(self);
    QObject.connect(self._hidetimer,SIGNAL("timeout()"),self._timed_reset);
    
  def connect_app_signals (self,app):
    """connects standard app signals to appropriate methods."""
    self._app = app;
    QObject.connect(app,PYSIGNAL("solver.begin"),self.xcurry(self.solver_begin,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("solver.iter"),self.xcurry(self.solver_iter,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("solver.end"),self.xcurry(self.solver_end,_argslice=slice(1,2)));
    QObject.connect(app,PYSIGNAL("isConnected()"),self.xcurry(self.reset));
    
  def _show (self,secs=60):
    """shows meter, and starts timer to hide after the specified number of
    seconds""";
    self._hidetimer.start(secs*1000,True);
    self._wlabel.show();
    self.show();
  
  def solver_begin (self,rec):
    """processes solver.begin record. Usually connected to a Solver.Begin signal""";
    self._app.statusbar.clear();
    if rec.num_tiles > 1:
      msg = "<b>%(node)s</b> p:%(num_spids)d t:%(num_tiles)d u:<b>%(num_unknowns)d</b>"%rec;
    else:
      msg = "<b>%(node)s</b> p:%(num_spids)d u:<b>%(num_unknowns)d</b>"%rec;
    self._wlabel.setText("<nobr>"+msg+"</nobr>");
    self._show();
    
  def solver_iter (self,rec):
    """processes solver.iter record. Usually connected to a Solver.Iter signal""";
    msg = "<b>%(node)s</b> i<b>%(iterations)d</b> fit:<b>%(fit).4g</b> r:<b>%(rank)d</b>/%(num_unknowns)d "%rec;
    if rec.num_tiles > 1:
      msg += "c:%(num_converged)d/%(num_tiles)d"%rec;
    self._wlabel.setText("<nobr>"+msg+"</nobr>");
    self._show();
    
  def solver_end (self,rec):
    """processes solver.end record. Usually connected to a Solver.End signal""";
    if rec.converged:
      color="darkgreen";
    else:
      color="red";
    rec.final_iter = "<font color=\"%s\">i<b>%d</b></font>"%(color,rec.iterations);
    msg = "<b>%(node)s</b> %(final_iter)s fit:<b>%(fit).4g</b> r:<b>%(rank)d</b>/%(num_unknowns)d "%rec;
    if rec.num_tiles > 1:
      msg += "c:%(num_converged)d/%(num_tiles)d"%rec;
#    if not rec.converged:
#      msg += " <b><font color=\"red\">N/C</font><b>";
    self._wlabel.setText("<nobr>"+msg+"</nobr>");
    self._show(20); # hide sooner when ended
    
  def _timed_reset (self):
    self.reset();
    
  def reset (self):
    """resets and hides meter."""
    self._wlabel.setText(""); 
    self._wlabel.hide();
    self.hide();
    self._hidetimer.stop();
