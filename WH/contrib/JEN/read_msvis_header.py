#!/usr/bin/python

# file: ../contrib/JEN/read_msvis_header.py

from Timba.meqkernel import set_state

def process_vis_header (hdr):
  """handler for the standard MS visheader""";
  # phase center
  (ra0,dec0) = hdr.phase_ref;
  set_state('ra0',value=ra0);
  set_state('dec0',value=dec0);
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
        set_state(label+'.'+sn,value=pos[j,iant]);
    except: pass;
  # array reference position
  for (j,label) in enumerate(coords):
    set_state(label+'0',value=pos[j,0]);

