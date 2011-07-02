# -*- coding: utf-8 -*-
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

import os

def spawnvp_wait (*args):
  """Equivalent to os.spawnvp(os.P_WAIT,*args)""";
  os.spawnvp(os.P_WAIT,*args);
 
def spawnvp_nowait (*args):
  """Equivalent to os.spawnvp(os.P_NOWAIT,*args), but closes all FDs in the child process
  except 0, 1 and 2. This is done to make sure all meqbrowser-inherited sockets are released""";
  # fork
  pid = os.fork();
  if pid:
    return pid;
  # child branch
  # close  all FDs so that sockets are not inherited 
  for fd in range(3,1024):
    try:
      os.close(fd);
    except:
      pass;
  os.execvp(*args);
  