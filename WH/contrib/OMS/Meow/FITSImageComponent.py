from Timba.TDL import *
from Timba.Meq import meq
from SixpackComponent import *

class FITSImageComponent (SixpackComponent):
  """FitsImageComponent is a sixpack component that uses the FITSImage node 
  to get an image from a FITS file.
  """;
  
  def __init__ (self,ns,name,filename,direction=None,cutoff=1.0,fluxscale=None):
    """Constructor args:
        ns:         the node scope
        name:       the source name
        filename:   FITS file name
        direction:  direction to source (a Direction object). If None, the
                    direction from the FITS file will be used.
        cutoff:     cutoff quotient. FITSImage will find the smallest box
          containing all points with cutoff*100% of the peak flux, and
          return only that box.
        fluxscale:  if specified, image flux will be rescaled by that factor
    """;
    SixpackComponent.__init__(self,ns,name,direction=direction,fluxscale=fluxscale);
    self._filename = str(filename);
    self._cutoff   = float(cutoff);
    
  def sixpack (self):
    image = self.ns.image;
    if not image.initialized():
      image <<= Meq.FITSImage(filename=self._filename,cutoff=self._cutoff);
    return image;
    
    
