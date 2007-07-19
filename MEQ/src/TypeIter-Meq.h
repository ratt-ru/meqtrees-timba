//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

    // This file is generated automatically -- do not edit
    // Regenerate using "make aids"
    #ifndef _TypeIter_Meq_h
    #define _TypeIter_Meq_h 1



#define DoForAllOtherTypes_Meq(Do,arg,separator) \
        

#define DoForAllBinaryTypes_Meq(Do,arg,separator) \
        

#define DoForAllSpecialTypes_Meq(Do,arg,separator) \
        

#define DoForAllIntermediateTypes_Meq(Do,arg,separator) \
        

#define DoForAllDynamicTypes_Meq(Do,arg,separator) \
        Do(Meq::Domain,arg) separator \
        Do(Meq::Cells,arg) separator \
        Do(Meq::Request,arg) separator \
        Do(Meq::Vells,arg) separator \
        Do(Meq::VellSet,arg) separator \
        Do(Meq::Result,arg) separator \
        Do(Meq::Funklet,arg) separator \
        Do(Meq::Polc,arg) separator \
        Do(Meq::ComposedPolc,arg) separator \
        Do(Meq::PolcLog,arg) separator \
        Do(Meq::Node,arg) separator \
        Do(Meq::Function,arg) separator \
        Do(Meq::Spline,arg)

#define DoForAllNumericTypes_Meq(Do,arg,separator) \
        
#endif
