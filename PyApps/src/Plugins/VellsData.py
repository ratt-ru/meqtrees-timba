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
from Timba.Plugins.plotting_functions import *

_dbg = verbosity(0,name='VellsData');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class VellsData:
   """ A class for handling and extracting Vells data for display """

   def __init__(self):
     self._active_plane = 0
     self._active_perturb = None

     self._plot_vells_dict = {}
     self._plot_flags_dict = {}
     self._plot_labels = {}
     self._key_menu_labels = {}
     self._menu_labels = {}
     self._perturbations_index = {}
     self._planes_index = []
     self.start_vells_id = 499
     self.array_selector = []
     self.array_tuple = None
     self.data_max = None
     self.data_min = None
     self.first_axis_parm = None
     self.second_axis_parm = None
     self.third_axis_parm = None
     self.initialSelection = False
     self.display_3D = False
     self.shape_change = True
     self.scalar_data = False
     self.rank = -1
     self.actual_rank = -1
     self.shape = (-1,)

#    self.__init__

   def calc_vells_ranges(self, vells_rec):
      """ this method determines the range of a vells. The results
          are used to set up proper axis labelling etc for the
          visualization displays.
      """
      self.axis_labels = []
      self.vells_axis_parms = {}
      self.vells_axis_grids = {}
      self.axis_shape = {}
      self.num_possible_ND_axes = 0
      try:
        axis_map = vells_rec.cells.domain.get('axis_map',['time','freq'])
        _dprint(3, 'axis map is ', axis_map)
        for i in range(len(axis_map)):
          # convert from Hiid to string
          current_label = str(axis_map[i]).lower()
          _dprint(3,' ')
          _dprint(3,'current label ', current_label)
          if current_label != '(null)':
            begin = 0
            end = 1
            grid_array = None
            title = current_label
            if vells_rec.cells.grid.has_key(current_label):
              try:
                grid_array = vells_rec.cells.grid.get(current_label)
                delta = vells_rec.cells.cell_size.get(current_label)
                # for the moment, assume all deltas are the same, 
                # so use first one
                try:
                  grid_step = 0.5 * delta[0]
                except:
                  grid_step = 0.5 * delta
                self.axis_shape[current_label] = grid_array.shape[0]
                _dprint(3, 'in calc_vells_ranges: grid_array shape is ', grid_array.shape)
                self.num_possible_ND_axes = self.num_possible_ND_axes + 1
                _dprint(3, 'in calc_vells_ranges: incrementing ND axes to ', self.num_possible_ND_axes)
                begin = grid_array[0] - grid_step
                if self.axis_shape[current_label] > 1:
                  end = grid_array[self.axis_shape[current_label] -1] + grid_step
                else:
                  end = grid_array[0] + grid_step
              except:
                self.axis_shape[current_label] = 1
              title = current_label
              if current_label == 'time':
                end = end - begin
                begin = 0
                title = 'Relative Time(sec)'
              if current_label == 'freq':
                if end >  1.0e6:
                  begin = begin / 1.0e6
                  end = end / 1.0e6
                  title = 'Frequency(MHz)'
                elif end >  1.0e3:
                  begin = begin / 1.0e3
                  end = end / 1.0e3
                  title = 'Frequency(KHz)'
                else:
                  title = 'Frequency(Hz)'
            else:
              self.axis_shape[current_label] = 1
            _dprint(3,'assigning self.vells_axis_parms key ', current_label)
            _dprint(3,'assigning begin ', begin)
            _dprint(3,'assigning end ', end)
            _dprint(3,'assigning title ', title)
            self.vells_axis_parms[current_label] = (begin, end, title, self.axis_shape[current_label])
            self.vells_axis_grids[current_label] = grid_array
            self.axis_labels.append(current_label)
      except:
      # we have no 'cells' field so need to create a fake one for
      # display purposes
        axis_map = ['time','freq']
        self.scalar_data = True
        for i in range(len(axis_map)):
          current_label = axis_map[i]
          begin = 0
          end = 0
          title = current_label
          if current_label == 'time':
            title = 'Relative Time(sec)'
          if current_label == 'freq':
            title = 'Frequency(MHz)'
          self.axis_shape[current_label] = 1
          self.vells_axis_parms[current_label] = (begin, end, title, self.axis_shape[current_label])
          self.vells_axis_grids[current_label] = None
          self.axis_labels.append(current_label)

      # do we request a ND GUI?
      if len(self.vells_axis_parms) > 2 and self.num_possible_ND_axes > 2:
        _dprint(3, '** in calc_vells_ranges:')
        _dprint(3, 'I think I need a ND GUI as number of valid plot axes is ',self.num_possible_ND_axes)
        _dprint(3, 'length of self.vells_axis_parms is ', len(self.vells_axis_parms))
      _dprint(3, 'self.vells_axis_parms is ', self.vells_axis_parms)
      _dprint(3, 'self.axis_labels is ', self.axis_labels)

    # calc_vells_ranges

   def getVellsDataParms(self):
     """ returns vells parameters for use with the visualization display """
     _dprint(3,'received method call')

     return [self.vells_axis_parms, self.axis_labels, self.num_possible_ND_axes,self.shape,self.vells_axis_grids]

   def StoreVellsData(self, vells_rec, rq_label = ''):
     """ converts vells record structure into a format that is
         easy to use with the visualization displays
     """
     self._plot_vells_dict = {}
     self._plot_flags_dict = {}
     self._plot_labels = {}
     self._menu_labels = {}
     self._perturbations_index = {}
     self._planes_index = []
     self.scalar_data = False
     self.scalar_string = ""
     self.rq_label = rq_label

     _dprint(3,' self.rq_label = ', self.rq_label)
     self.calc_vells_ranges(vells_rec)
     _dprint(3,'now after calc_vells_ranges')
     _dprint(3,'self.scalar_data ', self.scalar_data)
     if self.scalar_data and len(self.rq_label) > 0:
       self.scalar_string = self.rq_label + "\n"

     self._number_of_planes = len(vells_rec["vellsets"])
     _dprint(3, 'number of planes ', self._number_of_planes)
     id = self.start_vells_id
     self.dims = None
     self.index = []
     self.start_index = None
     if vells_rec.has_key("dims"):
       dims = vells_rec.dims
       self.dims = list(dims)
       for i in range(len(self.dims)):
         self.index.append(0)
       self.start_index = len(self.dims) - 1

# store data
     for i in range(self._number_of_planes):
       if vells_rec.vellsets[i].has_key("value"):
#        menu_label = "[" + str(i) + "] value" 
         menu_label = "[" + str(i) + "]" 
         if self.dims is None:
           text_display = menu_label
         else:
#          text_display = str(self.index) + " value" 
           text_display = str(self.index)
         id = id + 1
#        _dprint(3, 'menu label ', menu_label)
         self._menu_labels[id] = text_display
         self._key_menu_labels[id] = menu_label
         self._planes_index.append(id)
         self._plot_vells_dict[menu_label] = vells_rec.vellsets[i].value
#        _dprint(3, 'self._plot_vells_dict[menu_label] ', self._plot_vells_dict[menu_label])
         tag = "] main value "
         if self._number_of_planes > 1:
           if self.dims is None:
             plot_string = "[" + str(i) + tag 
           else:
             plot_string = str(self.index)
         else:
           if self.dims is None:
             plot_string = tag[2:len(tag)] 
           else:
             plot_string = str(self.index)
         if self.scalar_data:
           self.scalar_string = self.scalar_string + plot_string + " " + str(self._plot_vells_dict[menu_label]) + "\n"
         if len(self.rq_label) > 0:
           plot_string = plot_string + " " + self.rq_label
         self._plot_labels[menu_label] = plot_string
       
       if vells_rec.vellsets[i].has_key("perturbed_value"):
         try:
           number_of_perturbed_arrays = len(vells_rec.vellsets[i].perturbed_value)
           tag = "] perturbed value "
           perturbations_list = []
           perturbations_key = str(id) + ' perturbations'
           for j in range(number_of_perturbed_arrays):
             menu_label =  "[" + str(i) + tag + str(j) 
             if self.dims is None:
               text_display = menu_label
             else:
               text_display = str(self.index) + " perturbed value " + str(j)
             id = id + 1
             perturbations_list.append(id)
             self._menu_labels[id] = text_display
             self._key_menu_labels[id] = menu_label
             self._plot_vells_dict[menu_label] = vells_rec.vellsets[i].perturbed_value[j]
             if self._number_of_planes > 1:
               initial_plot_str = "[" + str(i) + tag + str(j)
             else:
               initial_plot_str = tag[2:len(tag)] + str(j)
       
             if len(self.rq_label) > 0:
               plot_string = initial_plot_str + " " + self.rq_label
             else:
               plot_string = initial_plot_str
             if self.scalar_data:
               self.scalar_string = self.scalar_string + plot_string + " " + str(self._plot_vells_dict[menu_label]) + "\n"
             self._plot_labels[menu_label] = plot_string
           self._perturbations_index[perturbations_key] = perturbations_list

         except:
           _dprint(3, 'The perturbed values cannot be displayed.')
# don't display message for the time being
#              Message =  'It would appear that there is a problem with perturbed values.\nThey cannot be displayed.'
#              mb_msg = QMessageBox("display_image.py",
#                               Message,
#                               QMessageBox.Warning,
#                               QMessageBox.Ok | QMessageBox.Default,
#                               QMessageBox.NoButton,
#                               QMessageBox.NoButton)
#              mb_msg.exec_loop()
       if vells_rec.vellsets[i].has_key("flags"):
         toggle_index = "flag data " + str(i)
         self._plot_flags_dict[toggle_index] = vells_rec.vellsets[i].flags

# update index used for strings on displays if self.dims exists
       if not self.dims is None:
         for j in range(self.start_index,-1,-1):
           if self.index[j] < self.dims[j] - 1:
             self.index[j] = self.index[j] + 1
             if j < self.start_index:
               for k in range(j+1, len(self.index)):
                 self.index[k] = 0
             break
           else:
             pass

# initialize axis selection ?
     if not self.initialSelection:
       tag = self._key_menu_labels[self.start_vells_id + 1]
       data = self._plot_vells_dict[tag]
       rank = data.rank
       shape = data.shape
       self.setInitialSelectedAxes(rank,shape)
       _dprint(3, 'called setInitialSelectedAxes')
   # end StoreVellsData

   def isVellsScalar(self):
     """ returns true if no cells structure so data must be scalar """
     _dprint(3,'returning self.scalar_data value ', self.scalar_data)
     return self.scalar_data

   def getScalarString(self):
     """ returns string of scalar values """
     return self.scalar_string

   def getShapeChange(self):
     """ returns true if data shape has changed """
     return self.shape_change

   def getNumPlanes(self):
     """ returns the number of vells planes that are stored """
     return self._number_of_planes

   def getMenuData(self):
     """ returns the labels for vells selection menu """
     return (self._menu_labels, self._perturbations_index, self._planes_index, self.dims)


   def getVellsPlotLabels(self):
     """ returns the labels for vells plot menu """
     return self._plot_menu_labels

   def activePlaneHasFlags(self):
     """ returns True if active plane has associated flags array """
     key = "flag data " + str(self._active_plane)
     if self._plot_flags_dict.has_key(key):
       return True
     else:
       return False

   def getActiveFlagData(self):
     """ returns flag data associated with active plane """
     key = "flag data " + str(self._active_plane)
     if self.array_tuple is None:
       return self._plot_flags_dict[key]
     else:
       return self._plot_flags_dict[key][self.array_tuple]

   def getActivePlane(self):
     """ returns number of active plane """
     return self._active_plane

   def getPlotLabels(self):
     """ returns the labels for vells plots """
     return self._plot_labels

   def getPlotLabel(self):
     """ returns the plot label for a given plane or perturbed plane """
     key = ""
     if not self._active_perturb is None:
       tag = "] perturbed value "
       key =  "[" + str(self._active_plane) + tag + str(self._active_perturb) 
     else:
       key = "[" + str(self._active_plane) + "]" 
     return self._plot_labels[key]

   def getActivePerturbData(self):
     """ returns the vells data for the perturbed data associated with
         the active plane
     """
     tag = "] perturbed value "
     key =  "[" + str(self._active_plane) + tag + str(self._active_perturb) 
     return self._plot_vells_dict[key]

   def getActiveData(self):
     key = ""
     if not self._active_perturb is None:
       tag = "] perturbed value "
       key =  "[" + str(self._active_plane) + tag + str(self._active_perturb) 
     else:
       key = "[" + str(self._active_plane) + "]" 
     rank = self._plot_vells_dict[key].rank
     shape = self._plot_vells_dict[key].shape
     if rank != self.rank or shape != self.shape:
       self.setInitialSelectedAxes (rank, shape)
     if self.array_tuple is None:
       return self._plot_vells_dict[key]
     else:
       _dprint(3, 'self.array_tuple ',  self.array_tuple)
       _dprint(3, 'self._plot_vells_dict[key][self.array_tuple] has rank ',  self._plot_vells_dict[key][self.array_tuple].rank)
       _dprint(3, 'self._plot_vells_dict[key][self.array_tuple] min and max: ', self._plot_vells_dict[key][self.array_tuple].min(), ' ', self._plot_vells_dict[key][self.array_tuple].max())
       return self._plot_vells_dict[key][self.array_tuple]

   def getActivePlot(self):
     return self._active_plane

   def getActiveDataRanks(self):
     _dprint(3, 'returning values elf.actual_rank, self.rank, self.shape ', self.actual_rank, ' ', self.rank, ' ', self.shape)
     return (self.actual_rank, self.rank, self.shape)

   def setActivePlane(self, active_plane=0):
     self._active_plane = active_plane

   def set_3D_Display(self, display_3D=False):
     self.display_3D = display_3D
     self.initialSelection = False

   def setInitialSelection(self, selection_flag=False):
     self.initialSelection = selection_flag

   def setActivePerturb(self, active_perturb=0):
     self._active_perturb = active_perturb

   def getActiveAxisParms(self):
     return [self.first_axis_parm, self.second_axis_parm, self.third_axis_parm]

   def unravelMenuId(self, menuid=0):
      id_string = self._key_menu_labels[menuid] 
      self._active_perturb = None
      self._active_plane = 0
      perturb_loc = id_string.find("perturbed value")
      str_len = len(id_string)
      if perturb_loc >= 0:
        self._active_perturb = int(id_string[perturb_loc+15:str_len])
      
      request_plane_string = '0'
      plane_loc = id_string.find("[")
      if plane_loc >= 0:
        closing_bracket = id_string.find("]")
        if closing_bracket >= 0:
          request_plane_string = id_string[plane_loc+1:closing_bracket]
        self._active_plane = int(request_plane_string)

   def unsetSelectedAxes (self):
     self.array_tuple = None
     self.array_selector = []
 
   def updateArraySelector (self,lcd_number, slider_value):
    if len(self.array_selector) > 0:
      self.array_selector[lcd_number] = slider_value
      self.array_tuple = tuple(self.array_selector)

   def setInitialSelectedAxes (self, rank, shape, reset=False):
     try:
       if not reset and rank == self.rank and self.shape == shape:
         self.shape_change = False
         return
       else:
         self.array_selector = []
         self.array_tuple = None
         first_axis = None
         second_axis = None
         third_axis = None
         self.first_axis_parm = None
         self.second_axis_parm = None
         self.third_axis_parm = None
         self.actual_rank = 0
         _dprint(3, 'self.actual_rank set ', self.actual_rank)
         self.rank = rank
         self.shape = shape
         self.shape_change = True
       _dprint(3, 'rank ', rank)
       _dprint(3, 'shape ', shape)
       _dprint(3, 'self.axis_labels ', self.axis_labels)
       _dprint(3, 'self.shape_change ', self.shape_change)
       for i in range(rank-1,-1,-1):
         _dprint(3, 'testing axes for shape[i] ', i, ' ', shape[i])
         if shape[i] > 1:
           self.actual_rank = self.actual_rank + 1
           _dprint(3, 'self.actual rank now ', self.actual_rank)
         if shape[i] > 1 and self.display_3D and third_axis is None:
           third_axis = i
           self.third_axis_parm = self.axis_labels[i]
         elif shape[i] > 1 and second_axis is None:
           second_axis = i
           self.second_axis_parm = self.axis_labels[i]
           _dprint(3, 'second axis becomes ', second_axis)
         elif shape[i] > 1 and first_axis is None:
           first_axis = i
           self.first_axis_parm = self.axis_labels[i]
           _dprint(3, 'first axis becomes ', first_axis)
       if rank > 2:
         if not first_axis is None and not second_axis is None:
           self.array_selector = create_array_selector(None, rank, shape, first_axis,second_axis,third_axis)
           self.array_tuple = tuple(self.array_selector)
         _dprint(3, 'array selector tuple ', self.array_tuple)
     except:
       _dprint(3, 'got an exception')
       self.array_selector = []
       self.array_tuple = None
     self.initialSelection = True
     _dprint(3, 'self.first_axis_parm ', self.first_axis_parm)
     _dprint(3, 'self.second_axis_parm ', self.second_axis_parm)
     _dprint(3, 'self.third_axis_parm ', self.third_axis_parm)

   def setSelectedAxes (self,first_axis, second_axis, third_axis=-1):
     self.array_selector = []
     self.array_tuple = None
     try:
       rank = self.getActiveData().rank
       if rank <= 2:
         return
       else:
         shape = self.getActiveData().shape
         self.array_selector = create_array_selector(None, rank, shape, first_axis,second_axis,third_axis)
         self.array_tuple = tuple(self.array_selector)
         for i in range(rank):
           if i == first_axis:
             self.first_axis_parm = self.axis_labels[i]
           elif i == second_axis:
             self.second_axis_parm = self.axis_labels[i]
           elif i == third_axis:
             self.third_axis_parm = self.axis_labels[i]
     except:
       self.array_selector = []
       self.array_tuple = None

   def getDataRange(self):
     return [self.data_max, self.data_min]

   def setDataRange(self):
     """ figure out minima and maxima of active array """
     data_array = self.getActiveData()
     if self.test_scalar(data_array):
       self.data_min = data_array
       self.data_max = data_array
     else:
       if data_array.type() == Complex32 or data_array.type() == Complex64:
         real_array = data_array.getreal()
         imag_array = data_array.getimag()
         real_min = real_array.min()
         real_max = real_array.max()
         imag_min = imag_array.min()
         imag_max = imag_array.max()
         if real_min < imag_min:
           self.data_min = real_min
         else:
           self.data_min = imag_min
         if real_max > imag_max:
           self.data_max = real_max
         else:
           self.data_max = imag_max
       else:
         self.data_min = data_array.min()
         self.data_max = data_array.max()

   def test_scalar(self, test_array):
     is_scalar = False
     try:
       shape = test_array.shape
     except:
       is_scalar = True
     return is_scalar

   
def main(args):
  print 'we are in main' 

# Admire
if __name__ == '__main__':
    main(sys.argv)

