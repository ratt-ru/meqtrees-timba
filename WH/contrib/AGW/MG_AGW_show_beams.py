#!/usr/bin/python

#
# Copyright (C) 2002-2007
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

# Short description:
# Read in and form X and Y voltage beams. Then create a composer node 
# that collects all the beams for display in a results plotter

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils
from make_multi_dim_request import *
from handle_beams import *

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_defocus','gauss_array_pats_offset','veidt_fpa_180', 'veidt_fpa_30'],more=str)

#setup a bookmark for display of results with a 'Result Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Results',page=[
    record(udi="/node/collector",viewer="Result Plotter",pos=(0,0))])]);

# to force caching put 100
Settings.forest_state.cache_policy = 100

########################################################
def _define_forest(ns):  

  num_beams = read_in_FPA_beams(ns,fpa_directory)
  BEAMS = range(0,num_beams)
  for k in BEAMS:
    ns.beam_y(k) << Meq.Sqrt(ns.image_re_yy(k) * ns.image_re_yy(k) + ns.image_im_yy(k) * ns.image_im_yy(k))
    ns.beam_x(k) << Meq.Sqrt(ns.image_re_xx(k) * ns.image_re_xx(k) + ns.image_im_xx(k) * ns.image_im_xx(k))
    ns.beam(k) << Meq.Composer(ns.beam_x(k),ns.beam_y(k))

  ns.collector << Meq.Composer( *[ns.beam(k) for k in BEAMS]);

########################################################################
def _test_forest(mqs,parent,wait=False):

# any large time and frequency range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 5000.0e6

  lm_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
  request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='collector',request=request),wait);
########################################################################

if __name__ == '__main__':
 # run in batch mode?
 if '-run' in sys.argv:
   from Timba.Apps import meqserver
   from Timba.TDL import Compile

   # this starts a kernel.
   mqs = meqserver.default_mqs(wait_init=10);

   # This compiles a script as a TDL module. Any errors will be thrown as
   # an exception, so this always returns successfully. We pass in
   # __file__ so as to compile ourselves.
   (mod,ns,msg) = Compile.compile_file(mqs,__file__);

   # this runs the _test_forest job.
   mod._test_forest(mqs,None,wait=True);
   print 'finished'
 else:
# Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

