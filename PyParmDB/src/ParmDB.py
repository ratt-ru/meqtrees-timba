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

from Timba.pyparmdb import *
from Timba.dmi import *
import os

class Parmdb:
    def __init__(self,name="test",type="aips"):
        self.reopen(name,type);

        
    def getParmNames(self,pattern="*"):
        if not self._db:
            print("no db opened, try reopen")
            return;
        names=getNames(self._db,pattern);
        #print "names",names;
        return names;

    def getRange(self,pattern="*"):
        if not self._db:
            print("no db opened, try reopen")
            return;
        domain=getRange(self._db,pattern);
        #print "names",names;
        return domain;

    def getFunklets(self,name,domain="all",parentId=-1):
        if not self._db:
            print("no db opened, try reopen")
            return;
        if domain == "all" or not isinstance(domain,dmi_type('MeqDomain',record)):
            funklets = getAllValues(self._db,name,parentId);
        else:
            funklets = getValues(self._db,name,domain,parentId);
        #print "funklets",funklets;
        return funklets;
        
    def reopen(self,name="test",type="aips"):
        self._name=name;
        if os.path.isdir(name):
            
            self._db=openParmDB(name,type,False);
        else:
            print(("path", name,"not existing. New parmdb will be created."));
            self._db=openParmDB(name,type,True);
        if not self._db:
            print(("Opening db",name,"FAILED"));
