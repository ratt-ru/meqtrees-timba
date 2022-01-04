#!/usr/bin/env python3


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
#
#  (c) 2013.				 (c) 2011.
#  National Research Council		 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6 		 Ottawa, Canada, K1A 0R6
#
#  This software is free software;	 Ce logiciel est libre, vous
#  you can redistribute it and/or	 pouvez le redistribuer et/ou le
#  modify it under the terms of	         modifier selon les termes de la
#  the GNU General Public License	 Licence Publique Generale GNU
#  as published by the Free		 publiee par la Free Software
#  Software Foundation; either	 	 Foundation (version 3 ou bien
#  version 2 of the License, or	 	 toute autre version ulterieure
#  (at your option) any later	 	 choisie par vous).
#  version.
#
#  This software is distributed in	 Ce logiciel est distribue car
#  the hope that it will be		 potentiellement utile, mais
#  useful, but WITHOUT ANY		 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the	 	 explicite ni implicite, y
#  implied warranty of			 compris les garanties de
#  MERCHANTABILITY or FITNESS FOR	 commercialisation ou
#  A PARTICULAR PURPOSE.  See the	 d'adaptation dans un but
#  GNU General Public License for	 specifique. Reportez-vous a la
#  more details.			 Licence Publique Generale GNU
#  					 pour plus de details.
#
#  You should have received a copy	 Vous devez avoir recu une copie
#  of the GNU General Public		 de la Licence Publique Generale
#  License along with this		 GNU en meme temps que ce
#  software; if not, contact the	 logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.	 cas, communiquez avec la Free
#  at http://www.fsf.org.		 Software Foundation, Inc. au
#						 http://www.fsf.org.
#
#  email:				 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca	 business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council		 Conseil national de recherches
#      Canada				    Canada
#  Herzberg Institute of Astrophysics	 Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.		 5071 West Saanich Rd.
#  Victoria BC V9E 2E7			 Victoria BC V9E 2E7
#  CANADA					 CANADA
#
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import numpy
HAS_TIMBA = False
try:
  from Timba.utils import verbosity
  _dbg = verbosity(0,name='SpectrumData');
  _dprint = _dbg.dprint;
  _dprintf = _dbg.dprintf;
  HAS_TIMBA = True
except:
  pass

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
     if HAS_TIMBA:
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
       axes = numpy.arange(incoming_data[i].ndim)[::-1]
       plot_array = numpy.transpose(incoming_data[i], axes)

# has plot array been stored?
       if len(self._plot_labels) == 0:
         self._menu_labels[0] = menu_label
         self._plot_labels[0] = plot_label
         self._combined_label_dict[0] = combined_display_label
         self._plot_dict[0] = plot_array
        
       else:
         plot_found = False
         if HAS_TIMBA:
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
       if HAS_TIMBA:
         _dprint(3,' creating combined array')
       shape = self._plot_dict[0].shape
       self.y_marker_step = shape[1]
       self.num_y_markers = plot_dict_size
       if HAS_TIMBA:
         _dprint(3,' self.y_marker_step ', self.y_marker_step)
       temp_array = numpy.zeros((shape[0], plot_dict_size * shape[1]),dtype=self._plot_dict[0].dtype)
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
  print('we are in main')

# Admire
if __name__ == '__main__':
    main(sys.argv)

