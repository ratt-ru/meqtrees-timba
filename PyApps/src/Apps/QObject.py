#
#% $Id: app_proxy.py 5418 2007-07-19 16:49:13Z oms $ 
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

from sets import Set

def PYSIGNAL (sig):
  """Emulates PYSIGNAL() in the absense of PyQt""";
  return sig;

class QObject (object):
  """This is a qt.QObject replacememt for systems with no PyQt.
  It supports a simple connect/emit mechanism."""
  def __init__ (name,*args):
    self._name = name;
    self._connections = {};
  def name (self):
    return self._name;
  
  def connect (sender,signal,receiver):
    """Connects named signal of sender to receiver""";
    conns = sender._connections.setdefault(signal,[]);
    conns.append(receiver);
    return True;
  connect = staticmethod(connect);
  
  def disconnect (sender,signal,receiver):
    """Disconnects named signal of sender from receiver""";
    conns = sender._connections.get(signal,None);
    if conns:
      sender._connections[signal] = filter(lambda x:x!=receiver,conns);
  disconnect = staticmethod(disconnect);
  
  def emit (signal,args):
    for receiver in self._connections.get(signal,[]):
      receiver(*args);
