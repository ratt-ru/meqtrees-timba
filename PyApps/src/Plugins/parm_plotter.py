#!/usr/bin/python

# modules that are imported
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


qtcolor = [Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta, Qt.yellow, Qt.darkRed, Qt.darkGreen, Qt.darkBlue, Qt.darkCyan, Qt.darkMagenta, Qt.darkYellow,Qt.black];



class MultipleScaleDraw(QwtScaleDraw):
  def __init__(self,scales):
    self.labels=scales;
    QwtScaleDraw.__init__(self);

  def label(self,v):
    max  = len(self.labels);
    if v-1 >= 0 and v-1 < max:
      v=self.labels[int(v-1)];

    return QwtScaleDraw.label(self,v)




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
    #    self._snippet_plotter.removeCurves()
    self._snippet_plotter.clear();


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
      ncy=len(coeffi[0]);
      if is_scalar(coeffi[0]):
        ncx=1;
        coeffi=[coeffi];
      else:
        ncx=len(coeffi);
    nr_spids=ncx*ncy;

    #define range of y-axis (A.U.)

    offsety = (range(1,nr_spids+1));
    scaley=zeros(nr_spids,Float64);
    
    long_polc = self._rec.solve_polc;
    rank = len(long_polc[0].coeff);
    lpcf = []; #long_polc coefficients
    for iplc in range(nr_spids):
      lpi=long_polc[iplc];
      lpcf.append(lpi.coeff);      
    x=[];
    y=[];
    miny=[];
    maxy=[];
    for icx in range(ncx):
      for icy in range(ncy):
        y.append([coeffi[icx][icy]]);
        miny.append(coeffi[icx][icy]);
        maxy.append(coeffi[icx][icy]);


        
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
          if coeffi[icx][icy] > maxy[ic]:
            maxy[ic]= coeffi[icx][icy];
          if coeffi[icx][icy] < miny[ic]:
            miny[ic]= coeffi[icx][icy];
          
          ic+=1;
          
      #      x.append(1./60.*(0.5*(domaini[1]+domaini[0])-offset));
      x.append((0.5*(domaini[1]+domaini[0])-offset));
      #      x.append((0.5*(domaini[1]+domaini[0])));



    #Now rescale y values and set labels for y-axis;
    labels=[0];


    for ic in range(nr_spids):
      scaley[ic]=(maxy[ic]-miny[ic]);

      if not miny[ic] == 0:
        if scaley[ic]/abs(miny[ic]) < 0.0001: #dont show ridiculous small variations
          scaley[ic]=1.;
      if scaley[ic]==0:
        scaley[ic]=1.;
      offsety[ic]*=2*scaley[ic];
      offsety[ic]-=miny[ic];
      for np in range(len(y[ic])):
        y[ic][np]+=offsety[ic];
        y[ic][np]/=scaley[ic];

      labels.append(miny[ic]);
  #    labels.append((miny[ic]+maxy[ic])*0.5);

      labels.append(maxy[ic]);
       

##    print "scaled with";
##    print scaley;
##    print offsety;
##    print "minimax"
##    print miny, maxy;






    fx=[];

    for spid in range(nr_spids):  
      fx.append(zeros(nr_x,Float64));
      for i in range(rank):
        rvrs= rank -1-i;
        fx[spid]+=lpcf[spid][rvrs]; #fit curve
        if rvrs>0 :
          fx[spid]=multiply(fx[spid],x);
      fx[spid]+=offsety[spid];
      fx[spid]/=scaley[spid];
      
    #      print y;
    #      print x;
    # now fill the plot with data

  
    self._snippet_plotter.setTitle('Snippet solution');
    for nrs in range(nr_spids):
      name = 'spid'+str(nrs);
      curve = self._snippet_plotter.insertCurve(name);
      self._snippet_plotter.setCurveSymbol(curve, QwtSymbol(
        QwtSymbol.Ellipse, QBrush(qtcolor[nrs%12]), QPen(qtcolor[((nrs/12)+12)%13]), QSize(7, 7)));
      self._snippet_plotter.setCurveData(curve, array(x), array(y[nrs]));
      self._snippet_plotter.setCurveStyle(curve,QwtCurve.NoCurve);
      name = 'fit' + '%(nrs)'
      # now add the curves of the fit
      fitcurve = self._snippet_plotter.insertCurve(name);
      self._snippet_plotter.setCurveStyle(fitcurve,QwtCurve.Spline);
      self._snippet_plotter.setCurveData(fitcurve, x, fx[nrs]);
      self._snippet_plotter.enableLegend(True,curve);	
      # add scales for miny, maxy


      #scaledraw.draw();
    self._snippet_plotter.setAxisTitle(QwtPlot.xBottom, "Time (rescaled)")
    self._snippet_plotter.setAxisTitle(QwtPlot.yLeft, "Parm Values ")

    #trick to define my own scalelabels (min max for every spid)
    #only works since my scale per definition runs from 2 to nr_spid*2+1

    self.scaledraw=MultipleScaleDraw(labels);
    self.scaledraw
    self.scaledraw.setScale(1,2*nr_spids+1,2*nr_spids+1,3);
    self._snippet_plotter.setAxisScaleDraw(QwtPlot.yLeft, self.scaledraw);

    self._snippet_plotter.setAxisScale(QwtPlot.yLeft,2,2*nr_spids+1,1);

   # self._snippet_plotter.enableYLeftAxis(False);
    
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
            self._visu_plotter = QwtImageDisplay('spectra',parent=self.wparent())
            self.set_widgets(self._visu_plotter,self.dataitem.caption,icon=self.icon())
            self._wtop = self._visu_plotter;     # QwtImageDisplay inherits from QwtPlot
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

