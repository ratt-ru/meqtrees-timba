# file .../contrib/JEN/Grunt/readme.py

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

"""The Grunt module has been developed for lowering the threshold for MeqTree users:

- MeqTree philosophy: create your own package, but use as much of
existing modules as possible. This requires us to offer the right
services (e.g. in the browser), and to suggest the kind of interfaces
that users find it easy to observe, so that they CAN share!

- Packaged functions (corrupt, correct)

- Collections of Jones matrices for different telescopes

  - Allows easy exchange between developers

- Simulation support (subtrees rather than MeqParms)

  - Defined with parameter groups

  - Deviation around the default value. a*cos(t/T)

  - Stddev of the simulation parameters a,T etc

  - Other deviation expressions

- Semi-automatic node naming (readability, uniqueness)

- Visualisation

  - Parameter values

  - Condeq residuals

  - Other nodes

- Parameter management (solving by named groups)

- Help

- Support for special solving schemes (peeling, redundancy)

- Interface with Meow system


"""
