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

__all__ = [ "dmi","utils","octopussy","octopython","dmi_repr" ];


# list of optional packages which will be added to the include path
_Packages = [ "Cattery" ];

# list of locations where packages will be searched for
_PackageLocations = [ "~",
  "/usr/local/MeqTrees","/usr/local/lib/MeqTrees","/usr/lib/MeqTrees",
  "/usr/local/meqtrees","/usr/local/lib/meqtrees","/usr/lib/meqtrees",
  ];




# mapping of package: path. Filled in as we find packages
_packages = {};

import sys
import os
import os.path

def packages ():
  """Returns mapping of available packages to their paths""";
  return _packages;
  # print "Using %s, set the %s_PATH environment variable to override this."%(path,package.upper());



def _tryPackageDir (path,package):
  """Tests if path refers to a valid directory, adds it to system include path if so.
  Marks package as having this path.""";
  if os.path.isdir(path):
    sys.path.insert(0,path);
    global _packages;
    _packages[package] = path;
    return True;
  return False;

def _setPackagePath (package):
  """Finds the given package, by first looking in $PACKAGE_PATH, then checking for 
  subdirectories of the standard _PackageLocations list.""";
  # check for explicit PACKAGE_PATH first
  path = os.environ.get('%s_PATH'%package.upper(),None);
  if path:
    if not _tryPackageDir(path,package):
      print "Warning: your %s_PATH environment variable is set to"%package.upper();
      print "%s, but this is not a valid directory."%path;
      print "The %s package will not be available."%package;
    return;
  # else look in standard places
  for path in _PackageLocations:
    path = os.path.expanduser(path);
    if _tryPackageDir(os.path.join(os.path.expanduser(path),package),package):
      return;
  # none found
  print "Warning: No %s package found."%package;
  print "If you have %s in a non-standard location, please set the %s_PATH environment"%(package,package.upper());
  print "variable to point to it."

for pkg in _Packages:
  _setPackagePath(pkg);