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

      #ifndef TID_MeqServer_h
      #define TID_MeqServer_h 1
      
      // This file is generated automatically -- do not edit
      // Regenerate using "make aids"
      #include <DMI/TypeId.h>

      // should be called somewhere in order to link in the registry
      int aidRegistry_MeqServer ();

#ifndef _defined_id_TpMeqPyNode
#define _defined_id_TpMeqPyNode 1
const DMI::TypeId TpMeqPyNode(-1705);             // from /home/oms/Timba/MeqServer/src/PyNode.h:10
const int TpMeqPyNode_int = -1705;
namespace Meq { class PyNode; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::PyNode> : public TypeTraits<Meq::PyNode>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPyNode_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::PyNode & ContainerReturnType;
                typedef const Meq::PyNode & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPyTensorFuncNode
#define _defined_id_TpMeqPyTensorFuncNode 1
const DMI::TypeId TpMeqPyTensorFuncNode(-1721);   // from /home/oms/Timba/MeqServer/src/PyTensorFuncNode.h:7
const int TpMeqPyTensorFuncNode_int = -1721;
namespace Meq { class PyTensorFuncNode; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::PyTensorFuncNode> : public TypeTraits<Meq::PyTensorFuncNode>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPyTensorFuncNode_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::PyTensorFuncNode & ContainerReturnType;
                typedef const Meq::PyTensorFuncNode & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSink
#define _defined_id_TpMeqSink 1
const DMI::TypeId TpMeqSink(-1481);               // from /home/oms/LOFAR/Timba/MeqServer/src/Sink.h:9
const int TpMeqSink_int = -1481;
namespace Meq { class Sink; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Sink> : public TypeTraits<Meq::Sink>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSink_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Sink & ContainerReturnType;
                typedef const Meq::Sink & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSpigot
#define _defined_id_TpMeqSpigot 1
const DMI::TypeId TpMeqSpigot(-1468);             // from /home/oms/LOFAR/Timba/MeqServer/src/Spigot.h:9
const int TpMeqSpigot_int = -1468;
namespace Meq { class Spigot; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Spigot> : public TypeTraits<Meq::Spigot>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSpigot_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Spigot & ContainerReturnType;
                typedef const Meq::Spigot & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqVisDataMux
#define _defined_id_TpMeqVisDataMux 1
const DMI::TypeId TpMeqVisDataMux(-1585);         // from /home/oms/LOFAR/Timba/MeqServer/src/VisDataMux.h:10
const int TpMeqVisDataMux_int = -1585;
namespace Meq { class VisDataMux; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::VisDataMux> : public TypeTraits<Meq::VisDataMux>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqVisDataMux_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::VisDataMux & ContainerReturnType;
                typedef const Meq::VisDataMux & ContainerParamType;
              };
            };
#endif


#endif
