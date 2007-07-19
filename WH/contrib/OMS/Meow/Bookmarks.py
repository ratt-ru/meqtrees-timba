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

from Timba.dmi import *
from Timba.TDL import *

_pages = [];

class Page (object):
  def __init__ (self,name,hplots=2,vplots=3):
    self.name = name;
    self.hsize = hplots;
    self.vsize = vplots;
    # find bookmarks list in Settings, or create new one
    self._bklist = Settings.forest_state.get('bookmarks',None);
    if self._bklist is None:
      self._bklist = Settings.forest_state.bookmarks = [];
    # page number, used when making multiple pages
    self._pagenum = 0;
    # make a new page record
    self._new_pagerec();
      
  def _new_pagerec (self):
    """creates a new, empty page record. Also used to advance a page.""";
    # make name 
    name = self.name;
    self._pagenum += 1;
    if self._pagenum > 1:
      name += ", Page "+str(self._pagenum);
    self._ix = self._iy = 0;
    # create basic record, but defer adding it to bookmarks
    # until we get at least one entry on the page
    self._pagelist = [];
    self._pagerec = record(name=name,page=self._pagelist);
    self._pagerec_added = False;
    
  def _add_pagerec (self):
    """adds page record to bookmarks, if not already added""";
    if not self._pagerec_added:
      self._bklist.append(self._pagerec);
      self._pagerec_added = True;
      
  def add (self,node,viewer="Result Plotter"):
    """Adds a panel to this page. 'node' is a node object or a node name.
    'viewer' may be used to override the default viewer type""";
    # resolve argument to node name
    if is_node(node):
      node = node.name;
    elif not isinstance(node,str):
      raise TypeError,"node or node name expected";
    # add page to bookmarks
    self._add_pagerec();
    # add bookmark
    self._pagelist.append(
      record(viewer=viewer,udi="/node/"+node,pos=(self._iy,self._ix))
    );
    self._ix += 1;
    if self._ix >= self.hsize:
      self._ix = 0;
      self._iy += 1;
      # have we filled up a page? start a new one
      if self._iy >= self.vsize:
        self._new_pagerec();
    return self;
        
  def __lshift__ (self,node):
    return self.add(node);
    
    

def PlotPage (name,*rows):
  bklist = [];
  
  if not isinstance(name,str):
    # must be just another row...
    rows = [name] + list(rows);
  
  for irow,onerow in enumerate(rows):
    for icol,node in enumerate(onerow):
      bklist.append(record(
        viewer="Result Plotter",
        udi="/node/"+node,
        pos=(irow,icol)));
        
  if not isinstance(name,str):
    return bklist;
  else:
    return record(name=name,page=bklist);
