from Timba.TDL import *
from Timba import pynode
from Timba.Meq import meq
from Timba import mequtils
import struct
import math

_dbg = utils.verbosity(0,name='digestif');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class DigestifACM (object):
  def __init__ (self,filename,freq_scale=1.0,freqaxis='freq'):
    infile = file(filename);
    header = infile.read(24);
    self.nel,self.nfreq,freq0,dfreq = struct.unpack('=iidd',header);
    freq0 *= freq_scale;
    dfreq *= freq_scale;
    self.domain = meq.gen_domain(**{freqaxis:[freq0-dfreq/2,freq0+(self.nfreq-.5)*dfreq]});
    self.cells = meq.gen_cells(self.domain,**{'num_'+freqaxis:self.nfreq});
    # read nfreq x nel x nel ACM from file
    self.acm = numarray.fromfile(infile,numarray.Complex64,
                                 shape=(self.nfreq,self.nel,self.nel));


class DigestifAcmNode (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    self.freqaxis = 'freq';

  def update_state (self,mystate):
    mystate('freqaxis');
    mequtils.add_axis(self.freqaxis);
    mystate('file_name');
    mystate('freq_scale',1.0);
  
  def get_result (self,request,*children):
    acm = DigestifACM(self.file_name,freq_scale=self.freq_scale,freqaxis=self.freqaxis);
    # create nel x nel freq vectors
    # first figure out shape of frequency vector
    iaxis = mequtils.get_axis_number(self.freqaxis);
    spshape = [1]*(iaxis+1);
    spshape[iaxis] = acm.nfreq;
    # make a result object
    result = meq.result(cells=acm.cells);
    result.dims = (acm.nel,acm.nel);
    result.vellsets = [];
    # now form up list of vellsets from each spectrum in the ACM
    for irow in range(acm.nel):
      for icol in range(acm.nel):
        vells = meq.vells(spshape,is_complex=True,value=acm.acm[:,icol,irow]);
        result.vellsets.append(meq.vellset(vells));
    #
    return result;


## this is for testing purposes
def _define_forest (ns,**kwargs):
  ns.acm << Meq.PyNode(class_name="DigestifAcmNode",module_name=__file__,
                       file_name='acm.bin',cache_policy=100);

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=10);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('acm',request);

