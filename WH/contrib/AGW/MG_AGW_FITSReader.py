#!/usr/bin/python


#% $Id: MG_AGW_FITSReader.py 3929 2006-09-01 20:17:51Z twillis $ 

#
# Copyright (C) 2006
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# script_name = 'MG_AGW_FITSReader.py'

# Short description:
#  The script should just read in a 2-D array of points from a
#  FITS file and assign them to a cell, which is independent of 
#  time and frequency, but knows about L and M.

# History:
# - 3 Oct 2006: creatiion:

#=======================================================================
# Import of Python / TDL modules:

import math
import random

from Timba.Trees import JEN_bookmarks

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

# Scripts needed to run a MG_JEN script:
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.MXM import MG_MXM_functional
from Timba.Contrib.JEN.util import JEN_bookmarks


# to force caching put 100
Settings.forest_state.cache_policy = 100


########################################################
def _define_forest(ns):  
    
 MG_MXM_functional._add_axes_to_forest_state(['L','M']);

 home_dir = os.environ['HOME']
 ns.dummy<<Meq.Parm([[0,1],[1,0]],node_groups='Parm')
 infile_name = home_dir + '/Timba/WH/contrib/AGW/demo.fits'
 image_root = ns.image << Meq.FITSImage(filename=infile_name,cutoff=1.0);
 reader_root = ns.reader << Meq.FITSReader(filename=infile_name);
 ns.reqseq << Meq.ReqSeq(ns.image, ns.reader, result_index=1)

 # Define Bookmarks
 JEN_bookmarks.create(image_root,page="Image",viewer="Result Plotter");
 JEN_bookmarks.create(reader_root,page="Image",viewer="Result Plotter");

########################################################################

def _test_forest(mqs,parent):

 # run dummy first, to make python know about the extra axes (some magic)
 MG_MXM_functional._dummy(mqs, parent);

 # Create the Request Cells
 time_range = [0.,1.]          # should be independent of time, for now
 freq_range = [0.,1.]          # should be independent of frequency, for now
 L_range = [-1., 1.0]
 M_range = [-1.0, 1.0]
 dom_range = [freq_range, time_range, L_range, M_range]
 nr_cells = [1, 1, 79, 79]
 request = MG_MXM_functional._make_request(Ndim=4, dom_range=dom_range,
                                             nr_cells=nr_cells)

 # And execute the Tree ...
 args=record(name='reqseq', request=request);
 mqs.meq('Node.execute', args, wait=False);
   

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
