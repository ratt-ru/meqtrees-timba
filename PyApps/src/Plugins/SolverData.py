#!/usr/bin/env python

import sys
from numarray import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='SolverData');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class SolverData:
   """ a class to store solver data and supply the
       data to the browser display """

   def __init__(self, data_label=''):
     self._data_label = data_label
     self._solver_array = None
     self.metrics_rank = None
     self.metrics_chi_0 = None
     self.solver_offsets = None
     self.metrics_unknowns = None
     self.chi_array = None
     self.chi_vectors = None
     self.nonlin = None
     self.prev_unknowns = 0
     self.iteration_number = None
#    self.__init__


   def StoreSolverData(self, incoming_data, data_label=''):
     """ This method stores the data """
     self._data_label = data_label
     if incoming_data.solver_result.has_key("incremental_solutions"):
       self._solver_array = incoming_data.solver_result.incremental_solutions
       self.chi_array = self._solver_array.copy()
       shape = self._solver_array.shape
       #shape[0] = number of interations == num_metrics (see below)
       #shape[1] = total number of solution elements
       if incoming_data.solver_result.has_key("metrics"):
         metrics = incoming_data.solver_result.metrics
# find out how many records in each metric field
         num_metrics = len(metrics)
         num_metrics_rec =  len(metrics[0])
         self.solver_offsets = zeros((num_metrics_rec), Int32)
         self.metrics_rank = zeros((num_metrics,num_metrics_rec), Int32)
         self.metrics_unknowns = zeros((num_metrics,num_metrics_rec), Int32)
         self.metrics_chi_0 = zeros((num_metrics,num_metrics_rec), Float64)
         self.chi_vectors = zeros((num_metrics,num_metrics_rec), Float64)
         self.iteration_number = zeros((num_metrics), Int32)
         for i in range(num_metrics):
           if i > 0:
             for j in range(shape[1]):
               self.chi_array[i,j] = self.chi_array[i,j] + self.chi_array[i-1,j]
           self.prev_unknowns = 0
           for j in range(num_metrics_rec):
             metrics_rec =  metrics[i][j]
             try:
               for k in range(self.prev_unknowns,self.prev_unknowns + metrics_rec.num_unknowns):
                  self.chi_vectors[i,j] = self.chi_vectors[i,j] + self.chi_array[i,k] * self.chi_array[i,k]
               self.chi_vectors[i,j] = sqrt(self.chi_vectors[i,j])
               self.metrics_rank[i,j] = metrics_rec.rank +self.prev_unknowns
               self.prev_unknowns = self.prev_unknowns + metrics_rec.num_unknowns
               self.metrics_chi_0[i,j] = metrics_rec.chi_0 
               self.metrics_unknowns[i,j] = metrics_rec.num_unknowns 
               if i == 0:
                 self.solver_offsets[j] = self.prev_unknowns
             except:
               pass
           self.iteration_number[i] = i+1
       if incoming_data.solver_result.has_key("debug_array"):
         debug_array = incoming_data.solver_result.debug_array
# find out how many records in each metric field
         num_debug = len(debug_array)
         num_nonlin =  len(debug_array[0].nonlin)
         self.nonlin = zeros((num_nonlin, num_debug), Float64)
         for j in range(num_debug):
           debug_rec = debug_array[j]
           nonlin = debug_rec.nonlin
           for i in range(num_nonlin):
             self.nonlin[i,j] = debug_rec.nonlin[i]

   def getSolverData(self):
     return self._solver_array

   def getSolverMetrics(self):
     #return (self.metrics_rank, self.iteration_number, self.solver_offsets, self.metrics_chi_0)
     return (self.metrics_rank, self.iteration_number, self.solver_offsets, self.chi_vectors, self.metrics_chi_0, self.nonlin)

def main(args):
  print 'we are in main' 

# Admire
if __name__ == '__main__':
    main(sys.argv)

