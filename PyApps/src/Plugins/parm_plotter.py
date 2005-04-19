#!/usr/bin/python

# modules that are imported
from math import pow

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from qt import *
from numarray import *
from Timba.Plugins.display_image import *
from Timba.Plugins.realvsimag import *
from Timba.Plugins.result_plotter import *



from Timba.utils import verbosity
_dbg = verbosity(0,name='parm_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class ParmPlotter(ResultPlotter):
  """ a class to visualize data of a Parameter, especially snippet solution , that is 
      contained within a node's record. Objects of 
      this class are launched from the meqbrowser GUI """

  _icon = pixmaps.bars3d
  viewer_name = "Parm Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    ResultPlotter.__init__(self,gw,dataitem,cellspec=cellspec);
    """ Instantiate HippoDraw objects that are used to control
        various aspects of plotting, if the hippo plotter
        is instantiated.
    """
    self._snippet_plotter = None
    
  def display_snippet_solution(self):
    """ fill plot with par_values per time_slot and line of solution polc """
    #clear plot
    self._snippet_plotter.removeCurves()


    offset=self._rec.solve_offset;
    parmdata = self._rec.parm_values;
    nr_x = len(parmdata);
    parmi=parmdata[0];
    coeffi=parmi.coeff;
    domaini=parmi.domain.time;  #change to general case....for now jsut use time

    if is_scalar(coeffi):
      coeffi=[[coeffi]];
      ncy=1;
      ncx=1;
    else :
      # again coeffi is a stupid numarray, so we have to to much more work to finally get the f. data...
      ncy=len(coeffi[0]);
      if is_scalar(coeffi[0]):
        ncx=1;
        coeffi=[coeffi];
      else:
        ncx=len(coeffi);
    nr_spids=ncx*ncy;
    long_polc = self._rec.solve_polc;
    rank = len(long_polc[0].coeff);
    lpcf = []; #long_polc coefficients
    for iplc in range(nr_spids):
      lpi=long_polc[iplc];
      lpcf.append(lpi.coeff);
    x=[];
    y=[];
    for icx in range(ncx):
      for icy in range(ncy):
        y.append([coeffi[icx][icy]]);
        
#    x.append(1./60.*(0.5*(domaini[1]+domaini[0])-offset)); 
    x.append((0.5*(domaini[1]+domaini[0])-offset)); 
#    x.append((0.5*(domaini[1]+domaini[0]))); 

    for idat in range(nr_x-1):
      parmi=parmdata[idat+1];
      coeffi=parmi.coeff;
      if is_scalar(coeffi):
        coeffi=[[coeffi]];
      if is_scalar(coeffi[0]):
        coeffi=[coeffi];
            
      domaini=parmi.domain.time;  #change to general case....for now jsut use time
      ic=0;
      for icx in range(ncx):
        for icy in range(ncy):
          y[ic].append(coeffi[icx][icy]);
          ic+=1;
#      x.append(1./60.*(0.5*(domaini[1]+domaini[0])-offset));
      x.append((0.5*(domaini[1]+domaini[0])-offset));
#      x.append((0.5*(domaini[1]+domaini[0])));

    fx=[];

    for spid in range(nr_spids):  
      fx.append(zeros(nr_x,Float64));
      for i in range(rank):
        rvrs= rank -1-i;
        fx[spid]+=lpcf[spid][rvrs]; #fit curve
        if rvrs>0 :
          fx[spid]=multiply(fx[spid],x);

    #      print y;
    #      print x;
    # now fill the plot with data
    self._snippet_plotter.setTitle('Snippet solution');
    for nrs in range(nr_spids):
      name = 'curve' + '%(nrs)' 
      curve = self._snippet_plotter.insertCurve(name);
      self._snippet_plotter.setCurveSymbol(curve, QwtSymbol(
        QwtSymbol.Ellipse, QBrush(Qt.red), QPen(Qt.red), QSize(7, 7)));
      self._snippet_plotter.setCurveData(curve, array(x), array(y[nrs]));
      self._snippet_plotter.setCurveStyle(curve,QwtCurve.NoCurve);
      name = 'fit' + '%(nrs)'
      # now add the curves of the fit
      fitcurve = self._snippet_plotter.insertCurve(name);
      self._snippet_plotter.setCurveData(fitcurve, x, fx[nrs]);
       

    self._snippet_plotter.setAxisTitle(QwtPlot.xBottom, "Time ")
    self._snippet_plotter.setAxisTitle(QwtPlot.yLeft, "Parm Values")
    self._snippet_plotter.replot();
    
        
      

        
  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    self._rec = dataitem.data;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if isinstance(self._rec, bool):
      return

    # there's a problem here somewhere ...
    if dmi_typename(self._rec) != 'MeqParm': # not a meqParm
    
      # AttributeError:
      # to do: a popup message here ...
      print 'not a parameter'
      # cached_result not found, display an empty viewer with a "no result
      # in this node record" message (the user can then use the Display with
      # menu to switch to a different viewer)
    else:
      if self._rec.has_key('auto_solve') and self._rec.auto_solve and self._rec.parm_values and self._rec.solve_polc:

        if self._snippet_plotter == None:
          self._snippet_plotter = QwtPlot('snippet solution',self.wparent());
          self.set_widgets(self._snippet_plotter,self.dataitem.caption,icon=self.icon())
          self._wtop = self._snippet_plotter;
          self._snippet_plotter.setAxisAutoScale(QwtPlot.xBottom)
          self._snippet_plotter.setAxisAutoScale(QwtPlot.yLeft)
          self._snippet_plotter.setAxisAutoScale(QwtPlot.yRight)

        self.display_snippet_solution();
      else:  #show cache result instead
        try: self._rec = self._rec.cache_result; # look for cached_result field
        except:
          # AttributeError:
          # to do: a popup message here ...
          print 'we ended at this exception'
          # cached_result not found, display an empty viewer with a "no result
          # in this node record" message (the user can then use the Display with
          # menu to switch to a different viewer)
        
        

          # are we dealing with Vellsets?
        if self._rec.has_key("vellsets"):
          if self._visu_plotter is None:
            self._visu_plotter = QwtImagePlot('spectra',parent=self.wparent())
            self.set_widgets(self._visu_plotter,self.dataitem.caption,icon=self.icon())
            self._wtop = self._visu_plotter;       # QwtImagePlot inherits from QwtPlot
          self._visu_plotter.plot_vells_data(self._rec)
          # otherwise we are dealing with a set of visualization data
        else:
           if self._rec.has_key("visu"):
             # do plotting of visualization data
             self.display_visu_data()
              
        # enable & highlight the cell
        self.enable();
        self.flash_refresh();
              
        _dprint(3, 'exiting set_data')
      
#Grid.Services.registerViewer(dmi_type('MeqResult',record),ParmPlotter,priority=10)
#Grid.Services.registerViewer(meqds.NodeClass('MeqDataCollect'),ParmPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass('MeqParm'),ParmPlotter,priority=23)
#Grid.Services.registerViewer(meqds.NodeClass(),ParmPlotter,priority=20)

