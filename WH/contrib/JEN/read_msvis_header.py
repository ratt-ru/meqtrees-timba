#!/usr/bin/python



from Timba import dmi
import meqserver

def setState (node,**fields):
  """helper function to set the state of a node specified by name or nodeindex"""
  rec = dmi.record(state=dmi.record(fields))
  if isinstance(node,str):
    rec.name = node
  elif isinstance(node,int):
    rec.nodeindex = node
  else:
    raise TypeError,'illegal node argumnent'
  # pass command to kernel
  meqserver.mqexec('Node.Set.State',rec)
  print '\n** read_msvis_header::setState():\n    ',rec,'\n'



def processVisHeader (hdr):
  """handler for the visheader"""

  print '\n** read_msvis_header::processVisHeader():'
  for key in hdr.keys():
    print '-',key,':',hdr[key]                    # see result below
  print
    
  # phase center
  (ra0,dec0) = hdr.phase_ref
  setState('ra0',value=ra0)
  setState('dec0',value=dec0)
  # antenna positions
  pos = hdr.antenna_pos
  if pos.rank != 2 or pos.shape[0] != 3:
    raise ValueError,'incorrectly shaped antenna_pos';
  nant = pos.shape[1]
  coords = ('x','y','z')
  for iant in range(nant):
    sn = str(iant+1)
    # since some antennas may be missing from the tree,
    # ignore errors
    try:
      for (j,label) in enumerate(coords):
        setState(label+'.'+sn,value=pos[j,iant])
    except: pass
  # array reference position
  for (j,label) in enumerate(coords):
    setState(label+'0',value=pos[j,0])

# register the handler with meqserver
meqserver.add_header_handler(processVisHeader)
  


#------------------------------------------------------------------
#   inputrec = dmi.record();
#   inputrec.sink_type = 'ms_in';
#   inputrec.ms_name = 'D1.MS';
#   inputrec.data_column_name = 'DATA';
#   inputrec.tile_size = 1;
#
#   inputrec.selection = dmi.record();
#   # inputrec.selection.channel_start_index = 0;
#   # inputrec.selection.channel_end_index = -1;
#   inputrec.selection.channel_start_index = 10;
#   inputrec.selection.channel_end_index = 50;
#   inputrec.python_init = 'read_msvis_header.py'
#   
#   outputrec = dmi.record();
#   outputrec.sink_type = 'ms_out';
#   outputrec.predict_column_name = 'PREDICT';
#   outputrec.residuals_column_name = 'RESIDUALS';
#   
#   initrec = dmi.record()
#   initrec.output_col = 'RESIDUALS'
#   
#   mqs.init(initrec, inputinit=inputrec, outputinit=outputrec);
#------------------------------------------------------------------


#==============================================================================
# ** read_msvis_header::processVisHeader():
# - selection : { channel_start_index: 10, channel_end_index: 50 }
# - tile_format : <conv_error>
# - channel_start_index : 10
# - flip_freq : True
# - channel_width : [ 312500.  312500.  312500.  312500.  312500.  312500.  312500.
#   312500.  312500.  312500.  312500.  312500.  312500.  312500.
#   312500.  312500.  312500.  312500.  312500.  312500.  312500.
#   312500.  312500.  312500.  312500.  312500.  312500.  312500.
#   312500.  312500.  312500.  312500.  312500.  312500.  312500.
#   312500.  312500.  312500.  312500.  312500.  312500.]
# - data_type : MS.Non.Calibrated
# - antenna_pos : [[ 3828763.10544699  3828746.54957258  3828729.99081359
#    3828713.43109885  3828696.86994428  3828680.31391933
#    3828663.75159173  3828647.19342757  3828630.63486201
#    3828614.07606798  3828609.94224429  3828603.73202612
#    3828460.92418735  3828452.64716351]
#  [  442449.10566454   442592.13950824   442735.17696417
#     442878.2118934    443021.24917264   443164.28596862
#     443307.32138056   443450.35604638   443593.39226634
#     443736.42941621   443772.19450029   443825.83321168
#     445059.52053929   445131.03744105]
#  [ 5064923.00777     5064923.00792     5064923.00829     5064923.00436
#    5064923.00397     5064923.00035     5064923.00204     5064923.0023
#    5064922.99755     5064923.          5064922.99868     5064922.99963
#    5064922.99071     5064922.98793   ]]
# - data_column_name : DATA
# - channel_freq : [  1.44437500e+09   1.44468750e+09   1.44500000e+09   1.44531250e+09
#    1.44562500e+09   1.44593750e+09   1.44625000e+09   1.44656250e+09
#    1.44687500e+09   1.44718750e+09   1.44750000e+09   1.44781250e+09
#    1.44812500e+09   1.44843750e+09   1.44875000e+09   1.44906250e+09
#    1.44937500e+09   1.44968750e+09   1.45000000e+09   1.45031250e+09
#    1.45062500e+09   1.45093750e+09   1.45125000e+09   1.45156250e+09
#    1.45187500e+09   1.45218750e+09   1.45250000e+09   1.45281250e+09
#    1.45312500e+09   1.45343750e+09   1.45375000e+09   1.45406250e+09
#    1.45437500e+09   1.45468750e+09   1.45500000e+09   1.45531250e+09
#    1.45562500e+09   1.45593750e+09   1.45625000e+09   1.45656250e+09
#    1.45687500e+09]
# - original_data_shape : [ 4 64]
# - num_antenna : 14
# - ddid_index : 0
# - field_index : 0
# - corr : ('XX', 'XY', 'YX', 'YY')
# - time : 4607179630.0
# - domain_index : -1
# - channel_end_index : 50
# - ms_name : D1.MS
# - cwd : /home/noordam/LOFAR/Timba/WH/contrib/JEN
# - phase_ref : [ 1.49488454  0.8700817 ]
# - vdsid : 0.0.0

# Traceback (most recent call last):
#   File "read_msvis_header.py", line 31, in processVisHeader
#     setState('ra0',value=ra0)
#   File "read_msvis_header.py", line 16, in setState
#     meqserver.mqexec('Node.Set.State',rec)
# octopython.OctoPythonError: node 'ra0' not found
#================================================================================
