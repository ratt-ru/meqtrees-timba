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
from Timba.Apps import assayer

import sys
import traceback
import os

# testing branch
if __name__ == '__main__':
  os.system("killall -9 meqserver meqserver-opt");
  
  ass = assayer.assayer("tdl_test");

  ass.compile("tdl_test.tdl");

  ass.init_test("default");

  ass.watch('x/cache.request_id');
  ass.watch('x/cache.result');

  ass.run();

  ass.inspect("x/cache.result");
  ass.inspect("solver/cache.result");

  stat = ass.finish();

  if stat:
    print("ASSAY FAILED: ",stat);
  else:
    print("ASSAY SUCCEEDED");
    
  
