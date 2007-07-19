#!/usr/bin/env python


#% $Id$ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import sys
from numarray import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='SpectrumData');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class SpectrumData:
   """ a class to store spectral data and supply the
       data to the browser display """

   def __init__(self, data_label='', string_tag=''):
     self._data_labels = data_label
     self._string_tag = string_tag
     self._active_plot = 0
     self.num_y_markers = 0
     self.y_marker_step = 0

     self._plot_dict = {}
     self._plot_labels = {}
     self._menu_labels = {}
     self._combined_label_dict = {}
     self.marker_labels = []

#    self.__init__


   def StoreSpectrumData(self, incoming_data):
     """ This method does most of the work. It stores the data,
         creates labels for the browser pull-down menu, and
         also creates titles for the plots """

     self._plot_dict = {}
     self._plot_labels = {}
     self._menu_labels = {}
     self._combined_label_dict = {}
     self.marker_labels = []

     num_plot_arrays = len(incoming_data)
     _dprint(2,' number of arrays to plot ', num_plot_arrays)
     for i in range(num_plot_arrays):
       menu_label = ''
       plot_label = ''
       combined_display_label = ''
       if isinstance(self._data_labels, tuple):
         menu_label = 'go to ' + self._string_tag  +  " " +self._data_labels[i] 
         combined_display_label = self._string_tag  +  " " + self._data_labels[i]
         plot_label = 'spectra:' + combined_display_label
       else:
         menu_label = 'go to ' + self._string_tag  +  " " +self._data_labels 
         combined_display_label = self._string_tag  +  " " + self._data_labels
         plot_label = 'spectra:' + combined_display_label

# flip plot array for screen display
       axes = arange(incoming_data[i].rank)[::-1]
       plot_array = transpose(incoming_data[i], axes)

# has plot array been stored?
       if len(self._plot_labels) == 0:
         self._menu_labels[0] = menu_label
         self._plot_labels[0] = plot_label
         self._combined_label_dict[0] = combined_display_label
         self._plot_dict[0] = plot_array
        
       else:
         plot_found = False
         _dprint(2,' plot_labels ', self._plot_labels)
         for j in range(len(self._plot_labels)):
           if self._plot_labels[j] == plot_label:
	     self._plot_dict[j] = plot_array
             plot_found = True
	     break
         if not plot_found:
           index = len(self._plot_labels)
	   self._plot_dict[index] = plot_array
           self._combined_label_dict[index] = combined_display_label
	   self._plot_labels[index] = plot_label
	   self._menu_labels[index] = menu_label

# create combined image?
     if len(self._plot_dict) > 1:
       plot_dict_size = len(self._plot_dict)
       _dprint(3,' creating combined array')
       shape = self._plot_dict[0].shape
       self.y_marker_step = shape[1]
       self.num_y_markers = plot_dict_size
       _dprint(3,' self.y_marker_step ', self.y_marker_step)
       temp_array = zeros((shape[0], plot_dict_size * shape[1]), self._plot_dict[0].type())
       for i in range(plot_dict_size):
         dummy_array =  self._plot_dict[i]
         for j in range(shape[0]):
           for k in range(shape[1]):
             k_index = i * shape[1] + k
             temp_array[j,k_index] = dummy_array[j,k]
         self.marker_labels.append(self._combined_label_dict[i])
       self._plot_dict[plot_dict_size] = temp_array
       self._plot_labels[plot_dict_size] = 'spectra: combined image'
       self._menu_labels[plot_dict_size] = 'go to combined image'

   def getMenuLabels(self):
     return self._menu_labels

   def getPlotLabels(self):
     return self._plot_labels

   def getPlotLabel(self):
     return self._plot_labels[self._active_plot]

   def getPlotData(self):
     return self._plot_dict

   def getPlotDictSize(self):
     return len(self._plot_dict)

   def getActivePlot(self):
     return self._active_plot

   def setActivePlot(self, active_plot=0):
     self._active_plot = active_plot

   def getActivePlotArray(self):
     return self._plot_dict[self._active_plot]

   def getMarkerParms(self):
     return [self.num_y_markers, self.y_marker_step] 

   def getMarkerLabels(self):
     return self.marker_labels

def main(args):
  print 'we are in main' 

# Admire
if __name__ == '__main__':
    main(sys.argv)

