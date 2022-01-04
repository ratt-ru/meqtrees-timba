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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import numpy
import math

try:
  from Timba.utils import verbosity
  _dbg = verbosity(0,name='SolverData');
  _dprint = _dbg.dprint;
  _dprintf = _dbg.dprintf;
except:
  pass

class SolverData:
   """ a class to store solver data and supply the
       data to the browser display """

   def __init__(self, data_label=''):
     self._data_label = data_label
     self._solver_array = None
     self.metrics_rank = None
     self.metrics_covar = None
     self.condition_numbers = None 
     self.cn_chi = None 
     self.metrics_chi_0 = None
     self.solver_offsets = None
     self.solver_labels = None
     self.metrics_unknowns = None
     self.chi_array = None
     self.eigenvectors = None
     self.vector_sum = None
     self.incr_soln_norm = None
     self.sum_incr_soln_norm = None
     self.nonlin = None
     self.prev_unknowns = 0
     self.iteration_number = None
#    self.__init__

   def StoreSolverData(self, incoming_data, data_label=''):
     """ This method stores solver data and calculates various
         arrays that describe the behaviour of the solver solutions
         as a function of iteration number
     """
     self.metrics_covar = None
     self._data_label = data_label
     if "incremental_solutions" in incoming_data.solver_result:
       self._solver_array = incoming_data.solver_result.incremental_solutions
       self.chi_array = self._solver_array.copy()
       shape = self._solver_array.shape
       #shape[0] = number of interations == num_metrics (see below)
       #shape[1] = total number of solution elements
       if "metrics" in incoming_data.solver_result:
         metrics = incoming_data.solver_result.metrics
# find out how many records in each metric field
         num_metrics = len(metrics)
         num_metrics_rec =  len(metrics[0])
         self.solver_offsets = numpy.zeros((num_metrics_rec), numpy.int32)
         self.metrics_rank = numpy.zeros((num_metrics,num_metrics_rec), numpy.int32)
         self.metrics_unknowns = numpy.zeros((num_metrics,num_metrics_rec), numpy.int32)
         self.metrics_covar = []
         self.metrics_chi_0 = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.metrics_chi = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.metrics_fit = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.metrics_mu = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.metrics_stddev = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.metrics_flag = numpy.zeros((num_metrics,num_metrics_rec), numpy.bool_)
         self.vector_sum = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.incr_soln_norm = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.sum_incr_soln_norm = numpy.zeros((num_metrics,num_metrics_rec), numpy.float64)
         self.iteration_number = numpy.zeros((num_metrics), numpy.int32)
         for i in range(num_metrics):
           if i > 0:
             for j in range(shape[1]):
               self.chi_array[i,j] = self.chi_array[i,j] + self.chi_array[i-1,j]
           self.prev_unknowns = 0
           # we just reset the following list for each iteration, so that
           # only the last one is actually used
           covar_list = []
           for j in range(num_metrics_rec):
             metrics_rec =  metrics[i][j]
             try:
               if "covar" in metrics_rec:
                 covar_list.append(metrics_rec.covar)
               self.metrics_chi_0[i,j] = metrics_rec.chi_0 
               self.metrics_fit[i,j] = metrics_rec.fit 
               self.metrics_chi[i,j] = metrics_rec.chi 
               self.metrics_mu[i,j] = metrics_rec.mu 
               self.metrics_flag[i,j] = metrics_rec.flag 
               self.metrics_stddev[i,j] = metrics_rec.stddev 
               sum_array = 0.0
               sum_array_test = 0.0
               for k in range(self.prev_unknowns,self.prev_unknowns + metrics_rec.num_unknowns):
                  sum_array_test = sum_array_test + self.chi_array[i,k] * self.chi_array[i,k]
                  self.vector_sum[i,j] = self.vector_sum[i,j] + self.chi_array[i,k] * self.chi_array[i,k]
                  sum_array = sum_array + self._solver_array[i,k] * self._solver_array[i,k]
               self.vector_sum[i,j] = math.sqrt(self.vector_sum[i,j])
               self.incr_soln_norm[i,j] = math.sqrt(sum_array)
               if i == 0:
                 self.sum_incr_soln_norm[i,j] = self.sum_incr_soln_norm[i,j] + self.incr_soln_norm[i,j] 
               else:
                 self.sum_incr_soln_norm[i,j] = self.sum_incr_soln_norm[i-1,j] + self.incr_soln_norm[i,j] 
               self.metrics_rank[i,j] = metrics_rec.rank +self.prev_unknowns
               self.prev_unknowns = self.prev_unknowns + metrics_rec.num_unknowns
               self.metrics_unknowns[i,j] = metrics_rec.num_unknowns 
               if i == 0:
                 self.solver_offsets[j] = self.prev_unknowns
             except:
               pass
           self.iteration_number[i] = i+1
         if len(covar_list) > 0:
           self.metrics_covar.append(covar_list)
       if "debug_array" in incoming_data.solver_result:
         debug_array = incoming_data.solver_result.debug_array
# find out how many records in each metric field
         num_debug = len(debug_array)
         num_nonlin =  len(debug_array[0].nonlin)
         self.nonlin = numpy.zeros((num_nonlin, num_debug), numpy.float64)
         for j in range(num_debug):
           debug_rec = debug_array[j]
           nonlin = debug_rec.nonlin
           for i in range(num_nonlin):
             self.nonlin[i,j] = debug_rec.nonlin[i]

# get spid information
       if "spid_map" in incoming_data.solver_result:
         spid_map = incoming_data.solver_result.spid_map
         spid_keys = list(spid_map.keys())
         spid_int_keys = []
         for i in range(len(spid_keys)):
           spid_int_keys.append(int(spid_keys[i]))
         spid_int_keys.sort()
#        print 'spid_map ', spid_map 
#        print 'spid_keys', spid_int_keys
         self.solver_labels = []
         for i in range(len(spid_keys)):
           spid_dict = spid_map[str(spid_int_keys[i])]
           name = ''
           if "name" in spid_dict:
             name = spid_dict["name"]
           coeff_index = ''
           if "coeff_index" in spid_dict:
             coeff_index = spid_dict["coeff_index"]
           label = name + ' ' + str(coeff_index) + ' '
           self.solver_labels.append(label)

   def processCovarArray(self):
     """ get condition number information out of co-variance array """

#    print 'self.metrics_covar ', self.metrics_covar
     self.condition_numbers = []
     self.cn_chi = []
     if self.metrics_covar is None:
       return False
     else:
       if len(self.metrics_covar)== 0:
         return False
       else:
         shape=self.metrics_chi.shape
         num_iter = len(self.metrics_covar)
         # just process the final record
         covar_list = self.metrics_covar[num_iter-1]
         num_covar_matrices = len(covar_list)
         for i in range(num_covar_matrices):
           covar = covar_list[i]
           if covar.min() == 0.0 and covar.max() == 0.0:
             self.condition_numbers.append(None)
             self.cn_chi.append(None)
           else:
             # following equation provided by Sarod
             cond_number=numpy.linalg.norm(covar,2)/numpy.linalg.norm(covar,-2);
             self.condition_numbers.append(cond_number)
             self.cn_chi.append(cond_number * self.metrics_chi[shape[0]-1,i])
         return True

   def calculateCovarEigenVectors(self):
     """ calculate eigenvalues and eigenvectors of co-variance matrix """

     try:
       import numpy.linalg as la
     except:
       return False
     if self.metrics_covar is None:
       return False
     else:
       if len(self.metrics_covar)== 0:
         return False
       else:
         num_iter = len(self.metrics_covar)
         # just process the final record
         covar_list = self.metrics_covar[num_iter-1]
         num_covar_matrices = len(covar_list)
         self.eigenvectors = []
         for i in range(num_covar_matrices):
           covar = covar_list[i]
           shape = covar.shape
           if covar.min() == 0.0 and covar.max() == 0.0:
             self.eigenvectors.append(None)
           elif shape[0] != shape[1]:
             self.eigenvectors.append(None)
           else:
             # gets both eigenvalues and eigenvectors
             self.eigenvectors.append(la.eig(covar))
             # for moment, just get eigenvalues
#            self.eigenvectors.append(la.eigvals(covar))
         return True

   def getConditionNumbers(self):
     """ return the covariance matrix condition numbers """
     return (self.condition_numbers,self.cn_chi)

   def getEigenVectors(self):
     """ return the eigenvalues and eigenvectors of the covariance matrix """
     return self.eigenvectors

   def getSolverLabels(self):
     """ return the solver labels for the display """
     return self.solver_labels

   def getSolverData(self):
     """ return the solver incremental solutions array """
     return self._solver_array

   def getSolverMetrics(self):
     """ return a tuple that contains the various solver metrics
         arrays that are plotted in the chi_sq surface display
     """
     return (self.metrics_rank, self.iteration_number, self.solver_offsets, self.vector_sum, self.metrics_chi_0, self.nonlin, self.sum_incr_soln_norm, self.incr_soln_norm, self.metrics_fit, self.metrics_chi, self.metrics_mu, self.metrics_flag, self.metrics_stddev,self.metrics_unknowns)

def main(args):
  print('we are in main') 

# Admire
if __name__ == '__main__':
    main(sys.argv)

