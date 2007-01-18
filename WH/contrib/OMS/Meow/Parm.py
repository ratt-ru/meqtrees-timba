from Timba.TDL import *
from Timba.Meq import meq
from numarray import *


class Parm (object):
  """
  A Meow.Parm is a parameter definition object. This is used in the Meow
  interfaces to specify that a given value is to be represented by a
  (potentially solvable) parameter. The rationale for this (as opposed to
  using a plain Meq.Parm) is that Meow components can then add their own 
  options to a parm before actually instantiating the node. Also, the
  same definition can apply to many different parameters.
  """
  def __init__ (self,value=0,tags=[],tiling=None,time_deg=0,freq_deg=0,**kw):
    """Creates a parameter definition.
    'value' is an initial value for the parameter. This can be a numeric
    constant or a polc.
    'tags' is a set of tags for the parameter, specified as a tuple/list, 
    or as a string with space-separated tags.
    'tiling' specifies a subtiled parm. If an int is given, then subtiling
    in time is assumed, otherwise it must be a full tiling specification
    in dmi.record form (e.g. dmi.record(time=2,freq=4))
    't_deg','f_deg': species that the parm should be a polynomial of the given
    order in time/frequency.
    """;
    self.value = value;
    # process tags
    if isinstance(tags,str):
      tags = tags.split(" ");
    else:
      if not isinstance(tags,(list,tuple)):
        raise TypeError,"'tags' argument should be a string, list or tuple";
      self.tags = list(tags);
    # process tiling
    if tiling is not None:
      if isinstance(tiling,int):
        tiling = dmi.record(time=tiling);
      elif not isinstance(tiling,dmi.record):
        raise TypeError,"'tiling' argument should be an int or dmi.record";
    # set up dict of default options...
    self.options = dict(tiling=tiling,
            shape=[time_deg+1,freq_deg+1],
            node_groups='Parm',
            use_previous=True);
    # ...and override with any keywords
    self.options.update(kw);
    
  def make (self,tags=[]):
    """Returns a definition for the Parm node, suitable for assigning with <<.
    Extra tags will be added""";
    if isinstance(tags,str):
      tags = tags.split(" ");
    else:
      if not isinstance(tags,(list,tuple)):
        raise TypeError,"'tags' argument should be a string, list or tuple";
      tags = list(tags);
    # if no extra tags are specified, return cached definition if possible
    if not tags:
      definition = getattr(self,'_definition',None);
      if definition:
        return definition;
    # make new definition
    definition = Meq.Parm(self.value,
                    tags=self.tags + tags,
                    **self.options);
    # cache if no extra tags
    if not tags:
      self._definition = definition;
    return definition;  
