###
### This script demonstrates the use of MeqResampler and MeqModRes nodes.
### You need to have some knowledge of MeqParm node to use this.
### For more information please visit
### http://lofar9.astron.nl/meqwiki/MeqResampler

from Timba.TDL import *
from Timba.Meq import meq
# to generate random numbers
import random

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []


def _define_forest (ns, **kwargs):
   # make some MeqParm nodes
   ns.r<<Meq.Parm(meq.array([[1,0.1,0.01],[-0.01,0.01,0.021]]))
   ns.i<<Meq.Parm(meq.array([[-1,0.1,-0.01],[0.01,0.01,-0.021]]))
   # we have a complex value
   ns.x<<Meq.ToComplex(ns.r,ns.i)

   # now modify the request  we send to the above nodes "Randomly", so
   # that we can resample!
   # num_cells: array of the shape to modify the request
   ns.y<<Meq.ModRes(children=ns.x,num_cells=[random.randint(0,100),random.randint(0,100)],)

   # attach a Resampler so we get the resampled result
   # mode:1 or 2
   # mode=1: Interpolation
   # mode=2: Integration, used only for visibility data
   ns.z<<Meq.Resampler(children=ns.y,mode=1)

   # make bookmarks for the result before and after resampling
   bm = record(name='original', viewer='Result Plotter',
               udi='/node/y', publish=True)
   Settings.forest_state.bookmarks.append(bm)
   bm = record(name='result', viewer='Result Plotter',
               udi='/node/z', publish=True)
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True


def _tdl_job_execute (mqs, parent):
    domain = meq.domain(1200,1600,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=20)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='z', request=request))
    return result
