#!/usr/bin/env python

import sys
from numarray import *

from Timba.utils import verbosity
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
     self._menu_labels = {}
     self.do_calc_vells_range = True
     self.array_selector = []
     self.array_tuple = None
     self.data_max = None
     self.data_min = None
     self.first_axis_parm = None
     self.second_axis_parm = None
     self.initialSelection = False
     self.rank = -1
     self.shape = (-1,)

#    self.__init__

   def calc_vells_ranges(self, vells_rec):
      """ get vells data ranges for use with other functions """
                                                                                
      self.do_calc_vells_range = False
      axis_map = vells_rec.cells.domain.get('axis_map',['time','freq'])
      self.axis_labels = []
      self.vells_axis_parms = {}
      self.axis_shape = {}
      self.num_possible_ND_axes = 0
      for i in range(len(axis_map)):
        # convert from Hiid to string
        self.axis_labels.append(str(axis_map[i]).lower())
        current_label = self.axis_labels[i]
        begin = 0
        end = 0
        title = current_label
        if vells_rec.cells.domain.has_key(current_label):
          begin = vells_rec.cells.domain.get(current_label)[0]
	  end = vells_rec.cells.domain.get(current_label)[1]
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
        if vells_rec.cells.grid.has_key(current_label):
          grid_array = vells_rec.cells.grid.get(current_label)
          _dprint(3, 'in calc_vells_ranges: examining cells.grid for label ', current_label)
#         _dprint(3, 'in calc_vells_ranges: grid_array is ', grid_array)
          try:
            self.axis_shape[current_label] = grid_array.shape[0]
            _dprint(3, 'in calc_vells_ranges: grid_array shape is ', grid_array.shape)
            self.num_possible_ND_axes = self.num_possible_ND_axes + 1
            _dprint(3, 'in calc_vells_ranges: incrementing ND axes to ', self.num_possible_ND_axes)
          except:
            self.axis_shape[current_label] = 1
        else:
          self.axis_shape[current_label] = 1
        self.vells_axis_parms[current_label] = (begin, end, title, self.axis_shape[current_label])

      # do we request a ND GUI?
      if len(self.vells_axis_parms) > 2 and self.num_possible_ND_axes > 2:
        _dprint(3, '** in calc_vells_ranges:')
        _dprint(3, 'I think I need a ND GUI as number of valid plot axes is ',self.num_possible_ND_axes)
        _dprint(3, 'length of self.vells_axis_parms is ', len(self.vells_axis_parms))
        _dprint(3, 'self.vells_axis_parms is ', self.vells_axis_parms)
        _dprint(3, 'I am emitting a vells_axes_labels signal which will cause the ND GUI to be constructed')

      _dprint(3, 'self.vells_axis_parms is ', self.vells_axis_parms)
      _dprint(3, 'self.axis_labels is ', self.axis_labels)

    # calc-vells_ranges

   def getVellsDataParms(self):
     return [self.vells_axis_parms, self.axis_labels, self.num_possible_ND_axes]

   def StoreVellsData(self, vells_rec):
     self._plot_vells_dict = {}
     self._plot_flags_dict = {}
     self._plot_labels = {}
     self._menu_labels = {}
     if self.do_calc_vells_range:
       self.calc_vells_ranges(vells_rec)

     self._number_of_planes = len(vells_rec["vellsets"])
     _dprint(3, 'number of planes ', self._number_of_planes)
     id = -1

# store data
     for i in range(self._number_of_planes):
       if vells_rec.vellsets[i].has_key("value"):
         menu_label = "go to plane " + str(i) + " value" 
         id = id + 1
#        _dprint(3, 'menu label ', menu_label)
         self._menu_labels[id] = menu_label
         self._plot_vells_dict[menu_label] = vells_rec.vellsets[i].value
#        _dprint(3, 'self._plot_vells_dict[menu_label] ', self._plot_vells_dict[menu_label])
         tag = " main value "
         self._plot_labels[menu_label] = " plane " + str(i) + tag
       
       if vells_rec.vellsets[i].has_key("perturbed_value"):
         try:
           number_of_perturbed_arrays = len(vells_rec.vellsets[i].perturbed_value)
           tag = " perturbed value "
           for j in range(number_of_perturbed_arrays):
             menu_label =  "   -> go to plane " + str(i) + tag + str(j) 
             id = id + 1
             self._menu_labels[id] = menu_label
             self._plot_vells_dict[menu_label] = vells_rec.vellsets[i].perturbed_value[j]
             if self._number_of_planes > 1:
               self._plot_labels[menu_label] = " plane " + str(i) + tag + str(j)
             else:
               self._plot_labels[menu_label] = tag + str(j)
       
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

# initialize axis selection ?
     if not self.initialSelection:
       tag = self._menu_labels[0]
       data = self._plot_vells_dict[tag]
       rank = data.rank
       shape = data.shape
       self.setInitialSelectedAxes(rank,shape)
       _dprint(3, 'called setInitialSelectedAxes')
   # end StoreVellsData

   def getNumPlanes(self):
     return self._number_of_planes

   def getMenuLabels(self):
     return self._menu_labels

   def getVellsPlotLabels(self):
     return self._plot_menu_labels

   def activePlaneHasFlags(self):
     key = "flag data " + str(self._active_plane)
     if self._plot_flags_dict.has_key(key):
       return True
     else:
       return False

   def getActiveFlagData(self):
     key = "flag data " + str(self._active_plane)
     if self.array_tuple is None:
       return self._plot_flags_dict[key]
     else:
       return self._plot_flags_dict[key][self.array_tuple]

   def getActivePlaneData(self):
     return self._plot_vells_dict["go to plane " + str(self._active_plane) + " value"] 

   def getActivePlane(self):
     return self._active_plane

   def getPlotLabels(self):
     return self._plot_labels

   def getPlotLabel(self):
     key = ""
     if not self._active_perturb is None:
       tag = " perturbed value "
       key =  "   -> go to plane " + str(self._active_plane) + tag + str(self._active_perturb) 
     else:
       key = "go to plane " + str(self._active_plane) + " value" 
     return self._plot_labels[key]

   def getActivePerturbData(self):
     tag = " perturbed value "
     key =  "   -> go to plane " + str(self._active_plane) + tag + str(self._active_perturb) 
     return self._plot_vells_dict[key]

   def getActiveData(self):
     key = ""
     if not self._active_perturb is None:
       tag = " perturbed value "
       key =  "   -> go to plane " + str(self._active_plane) + tag + str(self._active_perturb) 
     else:
       key = "go to plane " + str(self._active_plane) + " value" 
     rank = self._plot_vells_dict[key].rank
     shape = self._plot_vells_dict[key].shape
     if rank != self.rank or shape != self.shape:
       self.setInitialSelectedAxes (rank, shape)
     if self.array_tuple is None:
       return self._plot_vells_dict[key]
     else:
       _dprint(3, 'self.array_tuple ',  self.array_tuple)
       _dprint(3, 'self._plot_vells_dict[key][self.array_tuple] has rank ',  self._plot_vells_dict[key][self.array_tuple].rank)
       return self._plot_vells_dict[key][self.array_tuple]

   def getPlotData(self):
     return self._plot_dict

   def getActivePlot(self):
     return self._active_plane

   def setActivePlane(self, active_plane=0):
     self._active_plane = active_plane

   def setActivePerturb(self, active_perturb=0):
     self._active_perturb = active_perturb

   def getActivePlotArray(self):
     return self._plot_dict[self._active_plane]

   def getActiveAxisParms(self):
     return [self.first_axis_parm, self.second_axis_parm]

   def unravelMenuId(self, menuid=0):
      id_string = self._menu_labels[menuid] 
      self._active_perturb = None
      self._active_plane = 0
      perturb_loc = id_string.find("perturbed value")
      str_len = len(id_string)
      if perturb_loc >= 0:
        self._active_perturb = int(id_string[perturb_loc+15:str_len])
      plane_loc = id_string.find("go to plane")
      if plane_loc >= 0:
        self._active_plane = int( id_string[plane_loc+12:plane_loc+14])

   def unsetSelectedAxes (self):
     self.array_tuple = None
     self.array_selector = []
 
   def updateArraySelector (self,lcd_number, slider_value):
    if len(self.array_selector) > 0:
      self.array_selector[lcd_number] = slider_value
      self.array_tuple = tuple(self.array_selector)

   def setInitialSelectedAxes (self, rank, shape):
     self.array_selector = []
     self.array_tuple = None
     first_axis = None
     second_axis = None
     self.first_axis_parm = None
     self.second_axis_parm = None
     try:
       if rank == self.rank and self.shape == shape:
         return
       else:
         self.rank = rank
         self.shape = shape
       _dprint(3, 'rank ', rank)
       _dprint(3, 'shape ', shape)
       _dprint(3, 'self.axis_labels ', self.axis_labels)
       for i in range(rank):
         _dprint(3, 'testing axes for shape[i] ', i, ' ', shape[i])
         if shape[i] > 1 and first_axis is None:
#          _dprint(3, 'finding first axis for shape[i] ', shape[i])
           first_axis = i
           self.first_axis_parm = self.axis_labels[i]
#          _dprint(3, 'setting self.first_axis_parm ', self.first_axis_parm)
           axis_slice = slice(0,shape[first_axis])
           if rank > 2:
             self.array_selector.append(axis_slice)
         elif shape[i] > 1 and second_axis is None:
#          _dprint(3, 'finding second axis for shape[i] ', shape[i])
           second_axis = i
           self.second_axis_parm = self.axis_labels[i]
#          _dprint(3, 'setting self.second_axis_parm ', self.second_axis_parm)
           axis_slice = slice(0,shape[second_axis])
           if rank > 2:
             self.array_selector.append(axis_slice)
         else:
           if rank > 2:
             self.array_selector.append(0)
       if rank > 2:
         self.array_tuple = tuple(self.array_selector)
         _dprint(3, 'array selector tuple ', self.array_tuple)
     except:
       _dprint(3, 'got an exception')
       self.array_selector = []
       self.array_tuple = None
     self.initialSelection = True
     _dprint(3, 'self.first_axis_parm ', self.first_axis_parm)
     _dprint(3, 'self.second_axis_parm ', self.second_axis_parm)

   def setSelectedAxes (self,first_axis, second_axis):
     self.array_selector = []
     self.array_tuple = None
     try:
       rank = self.getActiveData().rank
       if rank <= 2:
         return
       else:
         shape = self.getActiveData().shape
         for i in range(rank):
           if i == first_axis:
             axis_slice = slice(0,shape[first_axis])
             self.array_selector.append(axis_slice)
             self.first_axis_parm = self.axis_labels[i]
           elif i == second_axis:
             axis_slice = slice(0,shape[second_axis])
             self.array_selector.append(axis_slice)
             self.second_axis_parm = self.axis_labels[i]
           else:
             self.array_selector.append(0)
         self.array_tuple = tuple(self.array_selector)
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

