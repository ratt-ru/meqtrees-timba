from Timba.TDL import *
from Timba import pynode
from Timba.Meq import meq
from Timba import mequtils
import struct
import math
import pyfits

_dbg = utils.verbosity(0,name='digestif');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

DEG = math.pi/180
ARCMIN = DEG/60;

class DigestifElementReader (object):
  """This class reads a Digestif element pattern file
  """;
  def __init__ (self,filename,lm_scale=DEG,freq_scale=1.0,
                xaxis='l',yaxis='m',freqaxis='freq'):
    infile = file(filename);
    header = infile.read(64);
    self.nel,nl,nm,nfreq,l0,m0,freq0,dl,dm,dfreq = struct.unpack('=iiiidddddd',header);
    l0 *= lm_scale;
    m0 *= lm_scale;
    dl *= lm_scale;
    dm *= lm_scale;
    freq0 *= freq_scale;
    dfreq *= freq_scale;
    # form up a domain and cells record. Skip the freq axis if size is 1
    kw_domain = { xaxis:[l0-dl/2,l0+(nl-.5)*dl],
                  yaxis:[m0-dm/2,m0+(nm-.5)*dm] };
    kw_cells  = { 'num_'+xaxis:nl,
                  'num_'+yaxis:nm };
    if nfreq > 1:
      kw_domain[freqaxis] = [freq0-dfreq/2,freq0+(nfreq-.5)*dfreq];
      kw_cells['num_'+freqaxis] = nfreq;
    self.domain = meq.gen_domain(**kw_domain);
    self.cells = meq.gen_cells(self.domain,**kw_cells);
    # read nfreq x nm x nl array from file,
    # transpose into nfreq x nl x nm
    self.beamdata = numarray.fromfile(infile,numarray.Complex64,
                                      shape=(nfreq,nm,nl)); 
    self.beamdata.transpose((0,2,1));

class DigestifElementNode (pynode.PyNode):
  def __init__ (self,*args):
    self.xaxis = 'l';
    self.yaxis = 'm';
    self.freqaxis = 'freq';
    pynode.PyNode.__init__(self,*args);

  def update_state (self,mystate):
    mystate('file_name');
    mystate('xaxis');
    mystate('yaxis');
    mystate('freqaxis');
    mequtils.add_axis(self.xaxis);
    mequtils.add_axis(self.yaxis);
    mequtils.add_axis(self.freqaxis);
  
  def get_result (self,request,*children):
    reader = DigestifElementReader(self.file_name,
                                   xaxis=self.xaxis,yaxis=self.yaxis,
                                   freqaxis=self.freqaxis);
    cells = reader.cells;
    beam = meq.vells(meq.shape(cells),is_complex=True,value=reader.beamdata);
    return meq.result(meq.vellset(beam),cells=cells);

## this is for testing purposes
def _define_forest (ns,**kwargs):
  for p in range(4):
    ns.elm(p) << Meq.PyNode(class_name="DigestifElementNode",module_name=__file__,
                       file_name='elementbeam_%d.bin'%p,
                       cache_policy=100);
  ns.root << Meq.Composer(*[ns.elm(p) for p in range(4)]);

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=10);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('root',request);

## for command-line testing
if __name__ == '__main__':
  reader = DigestifElementReader('elementbeam_0.bin');
  print "beam:",reader.beamdata;
  print "beam cells:",reader.cells;
  print "beam domain:",reader.cells.domain;
  print "beam array shape:",reader.beamdata.shape;
  