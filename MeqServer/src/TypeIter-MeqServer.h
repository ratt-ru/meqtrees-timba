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
    #ifndef _TypeIter_MeqServer_h
    #define _TypeIter_MeqServer_h 1



#define DoForAllOtherTypes_MeqServer(Do,arg,separator) \
        

#define DoForAllBinaryTypes_MeqServer(Do,arg,separator) \
        

#define DoForAllSpecialTypes_MeqServer(Do,arg,separator) \
        

#define DoForAllIntermediateTypes_MeqServer(Do,arg,separator) \
        

#define DoForAllDynamicTypes_MeqServer(Do,arg,separator) \
        Do(Meq::VisDataMux,arg) separator \
        Do(Meq::Sink,arg) separator \
        Do(Meq::Spigot,arg) separator \
        Do(Meq::PyNode,arg) separator \
        Do(Meq::PyTensorFuncNode,arg)

#define DoForAllNumericTypes_MeqServer(Do,arg,separator) \
        
#endif
