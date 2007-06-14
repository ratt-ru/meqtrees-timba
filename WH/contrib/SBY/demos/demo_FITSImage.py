###
### This demonstrates the use of FITSImage node.
### For more information, please visit
### http://lofar9.astron.nl/meqwiki/MeqImage
from Timba.TDL import *
from Timba.Meq import meq


Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



def _define_forest (ns, **kwargs):
   # just read a FITS file, 
   # cutoff=any value in the range 0 to 1.0
   # filename= any FITS file of an image
   ns.image<<Meq.FITSImage(filename="demo.fits",cutoff=0.2)

   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result', viewer='Result Plotter',
               udi='/node/image', publish=True)
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True



def _tdl_job_execute (mqs, parent):
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='image', request=request))
    return result
