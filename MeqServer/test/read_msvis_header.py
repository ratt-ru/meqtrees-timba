#!/usr/bin/python

from Timba import dmi
import meqserver

def setState (node,**fields):
  """helper function to set the state of a node specified by name or
  nodeindex""";
  rec = dmi.record(state=dmi.record(fields));
  if isinstance(node,str):
    rec.name = node;
  elif isinstance(node,int):
    rec.nodeindex = node;
  else:
    raise TypeError,'illegal node argumnent';
  # pass command to kernel
  meqserver.mqexec('Node.Set.State',rec);

def processVisHeader (hdr):
  """handler for the visheader""";
  # phase center
  (ra0,dec0) = hdr.phase_ref;
  setState('ra0',value=ra0);
  setState('dec0',value=dec0);
  # antenna positions
  pos = hdr.antenna_pos;
  if pos.rank != 2 or pos.shape[0] != 3:
    raise ValueError,'incorrectly shaped antenna_pos';
  nant = pos.shape[1];
  coords = ('x','y','z');
  for iant in range(nant):
    sn = str(iant+1);
    # since some antennas may be missing from the tree,
    # ignore errors
    try:
      for (j,label) in enumerate(coords):
        setState(label+'.'+sn,value=pos[j,iant]);
    except: pass;
  # array reference position
  for (j,label) in r
  enumerate(coords):
    setState(label+'0',value=pos[j,0]);

# register the handler with meqserver
meqserver.add_header_handler(processVisHeader);
  

