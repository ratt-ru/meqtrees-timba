
# pull this first to skip all GUI definitions and includes
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

from Timba.Apps import app_nogui

from Timba.Apps import meqserver
from Timba.TDL import Compile
from Timba.Meq import meqds

import sys
import traceback

# testing branch
if __name__ == '__main__':
  mqs = meqserver.default_mqs(wait_init=10);
  #  mqs = meqserver.default_mqs(wait_init=5,spawn=None); # if already running

  print('meqserver state:',mqs.current_server.state);

  (mod,ns,msg) = Compile.compile_file(mqs,'tdl_test.tdl');

  mod._test_forest(mqs,None);

  # sync=True makes sure all commands above have completed on the kernel side
  # before state is fetched
  state = mqs.getnodestate('solver',sync=True);
  req = state.request;

  res = mqs.execute('x',req,wait=True);

  print(res);

  meq.halt();