# script_name = 'MG_AGW_LMRaDec.py'

# Short description:
#   Tests the Meqtree LMRaDec node

# Keywords: ....

# Author: Tony Willis (AGW), DRAO

# History:
# - 18 Sept 2006: first version checked in

# Copyright: The MeqTree Foundation

# standard preamble

#% $Id$ 

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

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
 
# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

def _define_forest (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
# set up a sequence of nodes for testing of the LMRaDec node

# first define a field centre RA and DEC (in radians)
  ra = 1.0
  dec = 1.0
  ns.ra0 << Meq.Parm(ra,node_groups='Parm')
  ns.dec0 << Meq.Parm(dec,node_groups='Parm')

# then create a MeqComposer containing the field centre RA and DEC as children
  ns.RADec0 <<Meq.Composer(ns.ra0, ns.dec0)

# then define an L,M location (in radians) with respect to
# the field centre
  L_pos = -0.1   # radians
  M_pos =  0.5   # radians
  ns.l_pos << Meq.Parm(L_pos,node_groups='Parm')
  ns.m_pos << Meq.Parm(M_pos,node_groups='Parm')

# create a  MeqComposer containing L_pos and M_pos as children
  ns.LM <<Meq.Composer(ns.l_pos, ns.m_pos)
                                                                                
# we should now be able to create an LMRaDec node with the field
# centre RA and DEC and the L and M offsets as children.
# This node gives as output the RA and DEC corresponding to the
# specified L,M offset
  ns.LMRaDec << Meq.LMRaDec(radec_0=ns.RADec0, lm=ns.LM)

# the following call would cause the output Ra, Dec to be rotated
# by 1 radian 
  # ns.LMRaDec << Meq.LMRaDec(radec_0=ns.RADec0, lm=ns.LM, pos_ang=1.0)

# Finally, as a check: convert the resulting RA and DEC back to L,M
# with respect to the original field centre. This is done by
# creating an LMN node which has the field centre RA and DEC
# and the offset RA and DEC as children.
  ns.LMN << Meq.LMN(ns.RADec0, ns.LMRaDec)

def _test_forest (mqs,parent,wait=False):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;

####
# any old time and frequency domain will do
# time - cover one day
  t0 = 0.01;
  t1 = 86400.01;

# any old frequency
  f1 =  299792458.0;
  f0 = 0.9*f1;

####
# Make cells array - a period of one day divided into 120 segments

  cells = meq.cells(meq.domain(f0,f1,t0,t1),num_freq=1,num_time=120);

# define request 
  request = meq.request(cells,rqtype='e1')

# execute request
  a = mqs.meq('Node.Execute',record(name='LMN',request=request),wait=wait);

# The following is the testing branch, executed when the script is run directly
# via 'python script.py'
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

 else:
  Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

