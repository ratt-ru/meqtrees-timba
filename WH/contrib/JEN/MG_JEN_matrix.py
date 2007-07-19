# MG_JEN_matrix.py

# Short description:
#   Some useful matrix subtrees 

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 

#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

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

from Timba.TDL import *

MG = record(script_name='MG_JEN_matrix.py', last_changed = 'h22sep2005')

from numarray import *

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG.script_name)






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   # Test/demo of importable function: rotation()
   bb = []
   angle1 = ns.angle1('3c84', x=4, y=5) << Meq.Constant(3)
   # angle2 = ns.angle2(y=5) << Meq.Constant(-1)
   angle2 = -1
   bb.append(rotation (ns, angle1))
   bb.append(rotation (ns, [angle2]))
   bb.append(rotation (ns, [angle1, angle2]))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.rotation()'))

   # Test/demo of importable function: ellipticity()
   bb = []
   angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
   angle2 = ns.angle2(y=5) << Meq.Constant(-1)
   bb.append(ellipticity (ns, angle1))
   bb.append(ellipticity (ns, [angle2]))
   bb.append(ellipticity (ns, [angle1, angle2]))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.ellipticity()'))
   
   # Test/demo of importable function: phase()
   bb = []
   angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
   angle2 = ns.angle2(y=5) << Meq.Constant(-1)
   bb.append(phase (ns, angle1))
   bb.append(phase (ns, [angle2]))
   bb.append(phase (ns, [angle1, angle2]))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.phase()'))


   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************

#------------------------------------------------------------
# Make a 2x2 rotation matrix

def rotation (ns, angle=0, qual=None, name='rotation_matrix'):

    # If no qual supplied, make a unique one:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_matrix_rotation', qual)

    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = (ns << Meq.Cos(a2))
        sin2 = (ns << Meq.Sin(a2))
        sin1 = (ns << Meq.Sin(a1))
        sin1 = (ns << Meq.Negate(sin1))
    else:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = cos1
        sin2 = (ns << Meq.Sin(a1))
        sin1 = (ns << Meq.Negate(sin2))
 
    # Compose the 2x2 matrix:
    mat = (ns[name].qmerge(cos1, sin1, sin2, cos2)(qual) << Meq.Composer(
		children=[cos1, sin1, sin2, cos2], dims=[2,2]))

    return mat


#------------------------------------------------------------
# Make a 2x2 ellipticity matrix

def ellipticity (ns, angle=0, qual=None, name='ellipticity_matrix'):

    # If no qual supplied, make a unique one:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_matrix_ellipticity', qual)

    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = (ns << Meq.Cos(a2))
        sin1 = (ns << Meq.Sin(a1))
        sin2 = (ns << Meq.Sin(a2))
        isin1 = (ns << Meq.ToComplex(0, sin1))
        isin2 = (ns << Meq.ToComplex(0, sin2))
        isin2 = (ns << Meq.Conj(isin2))

    else:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = cos1
        sin = (ns << Meq.Sin(a1))
        isin2 = (ns << Meq.ToComplex(0, sin))
        isin1 = isin2

    # Compose the 2x2 matrix:
    mat = (ns[name].qmerge(cos1,isin1, isin2, cos2)(qual) << Meq.Composer(
	children=[cos1, isin1, isin2, cos2], dims=[2,2]))

    return mat

#------------------------------------------------------------
# Make a 2x2 phase matrix

def phase (ns, angle=0, qual=None, name='phase_matrix'):

    # If no qual supplied, make a unique one:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_matrix_phase', qual)

    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        m11 = (ns << Meq.Polar(1, a1))
        m22 = (ns << Meq.Polar(1, a2))

    else:
        m11 = (ns << Meq.Polar(1, a1/2))
        m22 = (ns << Meq.Polar(1, ns << Meq.Negate(a1/2)))

    # Compose the 2x2 matrix:
    mat = (ns[name].qmerge(m11, m22)(qual) << Meq.Composer(
           children=[m11, 0, 0, m22], dims=[2,2]))
    return mat





#********************************************************************************
# Test routines
#********************************************************************************


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    print '\n**',MG.script_name,':\n'

    if 1:
        # This is the default:
        MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest)

    ns = NodeScope()

    if 0:
       rr = rotation (ns, angle=1)
       MG_JEN_exec.display_subtree (rr, 'MG_JEN_matrix::rotation', full=1)
          
    if 1:
       rr = ellipticity (ns, angle=1)
       MG_JEN_exec.display_subtree (rr, 'MG_JEN_matrix::ellipticity', full=1)
          
    if 1:
       rr = phase (ns, angle=1)
       MG_JEN_exec.display_subtree (rr, 'MG_JEN_matrix::phase', full=1)
          
    print '\n** end of',MG.script_name,'\n'

#********************************************************************************




