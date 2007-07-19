#!/usr/bin/python

# file: ../Timba/PyApps/src/Trees/read_MS_auxinfo.py
# Reads the OMS dmi header from the MS
# It is read automatically by the MeqKernel when the MS is opened.
# The file name is conveyed to the kernel via (see MG_JEN_exec.py):

#    path = os.environ['HOME']+'/LOFAR/Timba/PyApps/src/Trees/'
#    inputinit.python_init = path+'read_MS_auxinfo.py'

# NB: This should perhaps be in another 'official' MeqTree directory...

# Derived from OMS: ../Timba/MeqServer/test/read_msvis_header.py
#   See also the newer version: ../contrib/OMS/Meow/ReadVisHeader.py
# To be turned into a WSRT-specific version: read_WSRT_auxinfo.py



# from Timba.TDL import *
# from Timba.Meq import meq                     # required in MG_JEN_exec !!

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.meqkernel import set_state
from Timba.Contrib.JEN.util import TDL_radio_conventions


def process_vis_header (hdr):
  """handler for the standard MS visheader""";
  try:
    trace = True
    if trace: print '\n** read_MS_auxinfo.process_vis_header():'

    # Attach the header record ot the forest state record:
    # NB: This does not work, because this function is called too late...
    ## Settings.forest_state.vis_header = hdr

    # phase center
    (ra0,dec0) = hdr.phase_ref;
    if trace: print '- ra0 =',ra0
    if trace: print '- dec0 =',dec0
    try:
      set_state('ra0',value=ra0);
      set_state('dec0',value=dec0);
    except: pass;

    # time extent
    (t0,t1) = hdr.time_extent;
    if trace: print '- time extent: ',t0,t1;
    try:
      set_state('time0',value=t0);
      set_state('time1',value=t1);
    except: pass;

    # freq range
    f0,f1 = hdr.channel_freq[0],hdr.channel_freq[-1];
    if trace: print '- freq range: ',f0,f1;
    try:
      set_state('freq0',value=f0);
      set_state('freq1',value=f1);
    except: pass;

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
          if True:
            set_state(name, value=value)
      except: pass
      first = False

    if trace: print '** End of read_MS_auxinfo.process_vis_header() **\n'
    return True
  except:
    traceback.print_exc();
    return False

#----------------------------------------------------------------------





