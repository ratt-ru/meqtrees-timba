#!/usr/bin/python

# file: ../Timba/PyApps/src/Trees/read_MS_auxinfo.py
# Reads the OMS dmi header from the MS
# It is read automatically by the MeqKernel when the MS is opened.
# The file name is conveyed to the kernel via (see MG_JEN_exec.py):

#    path = os.environ['HOME']+'/LOFAR/Timba/PyApps/src/Trees/'
#    inputinit.python_init = path+'read_MS_auxinfo.py'

# NB: This should perhaps be in another 'official' MeqTree directory...

# Derived from OMS: ../Timba/MeqServer/test/read_msvis_header.py
# To be turned into a WSRT-specific version: read_WSRT_auxinfo.py


from Timba.meqkernel import set_state
from Timba.Trees import TDL_radio_conventions


def process_vis_header (hdr):
  """handler for the standard MS visheader""";

  trace = True
  if trace: print '\n** process_vis_header():'

  # phase center
  (ra0,dec0) = hdr.phase_ref;
  set_state('ra0',value=ra0);
  set_state('dec0',value=dec0);
  if trace: print '- ra0 =',ra0
  if trace: print '- dec0 =',dec0

  # antenna positions
  pos = hdr.antenna_pos;
  if pos.rank != 2 or pos.shape[0] != 3:
    raise ValueError,'incorrectly shaped antenna_pos';

  nant = pos.shape[1]
  stations = range(nant)
  coords = ['xpos','ypos','zpos']
  refpos = dict(xpos=0, ypos=0, zpos=0)
  first = True
  for station in stations:
    skey = TDL_radio_conventions.station_key(station)
    # Since some antennas may be missing from the tree, ignore errors
    try:
      for (j,label) in enumerate(coords):
        name = label+':s='+skey
        value = pos[j,station]
        if first: refpos[label] = value
        if trace: print '-',j,name,':',value,'  (relative =',value-refpos[label],')'
        set_state(name, value=value)
    except: pass
    first = False

  if trace: print '** End of process_vis_header() **\n'
  return True






#-------------------------------------------------------------

def process_vis_header_old (hdr):
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

