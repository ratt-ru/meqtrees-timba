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
     self.prev_unknowns = 0
     self.iteration_number = None
#    self.__init__


   def StoreSolverData(self, incoming_data, data_label=''):
     """ This method stores the data """
     self._data_label = data_label
     if incoming_data.solver_result.has_key("incremental_solutions"):
       self._solver_array = incoming_data.solver_result.incremental_solutions
       if incoming_data.solver_result.has_key("metrics"):
         metrics = incoming_data.solver_result.metrics
# find out how many records in each metric field
         num_metrics = len(metrics)
         num_metrics_rec =  len(metrics[0])
         self.metrics_rank = zeros((num_metrics,num_metrics_rec), Int32)
         self.iteration_number = zeros((num_metrics), Int32)
         for i in range(num_metrics):
           self.prev_unknowns = 0
           for j in range(num_metrics_rec):
             metrics_rec =  metrics[i][j]
             try:
               self.metrics_rank[i,j] = metrics_rec.rank +self.prev_unknowns
               self.prev_unknowns = metrics_rec.num_unknowns
             except:
               pass
           self.iteration_number[i] = i+1

   def getSolverData(self):
     return self._solver_array

   def getSolverMetrics(self):
     return (self.metrics_rank, self.iteration_number)

def main(args):
  print 'we are in main' 

# Admire
if __name__ == '__main__':
    main(sys.argv)

