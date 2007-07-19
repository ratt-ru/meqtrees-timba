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

      #ifndef TID_Meq_h
      #define TID_Meq_h 1
      
      // This file is generated automatically -- do not edit
      // Regenerate using "make aids"
      #include <DMI/TypeId.h>

      // should be called somewhere in order to link in the registry
      int aidRegistry_Meq ();

#ifndef _defined_id_TpMeqCells
#define _defined_id_TpMeqCells 1
const DMI::TypeId TpMeqCells(-1339);              // from /home/oms/LOFAR/Timba/MEQ/src/Cells.h:35
const int TpMeqCells_int = -1339;
namespace Meq { class Cells; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Cells> : public TypeTraits<Meq::Cells>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCells_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Cells & ContainerReturnType;
                typedef const Meq::Cells & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqComposedPolc
#define _defined_id_TpMeqComposedPolc 1
const DMI::TypeId TpMeqComposedPolc(-1582);       // from /home/oms/LOFAR/Timba/MEQ/src/ComposedPolc.h:9
const int TpMeqComposedPolc_int = -1582;
namespace Meq { class ComposedPolc; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ComposedPolc> : public TypeTraits<Meq::ComposedPolc>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqComposedPolc_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ComposedPolc & ContainerReturnType;
                typedef const Meq::ComposedPolc & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqDomain
#define _defined_id_TpMeqDomain 1
const DMI::TypeId TpMeqDomain(-1294);             // from /home/oms/LOFAR/Timba/MEQ/src/Domain.h:30
const int TpMeqDomain_int = -1294;
namespace Meq { class Domain; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Domain> : public TypeTraits<Meq::Domain>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqDomain_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Domain & ContainerReturnType;
                typedef const Meq::Domain & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFunction
#define _defined_id_TpMeqFunction 1
const DMI::TypeId TpMeqFunction(-1283);           // from /home/oms/LOFAR/Timba/MEQ/src/Function.h:29
const int TpMeqFunction_int = -1283;
namespace Meq { class Function; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Function> : public TypeTraits<Meq::Function>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFunction_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Function & ContainerReturnType;
                typedef const Meq::Function & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFunklet
#define _defined_id_TpMeqFunklet 1
const DMI::TypeId TpMeqFunklet(-1321);            // from /home/oms/LOFAR/Timba/MEQ/src/Funklet.h:31
const int TpMeqFunklet_int = -1321;
namespace Meq { class Funklet; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Funklet> : public TypeTraits<Meq::Funklet>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFunklet_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Funklet & ContainerReturnType;
                typedef const Meq::Funklet & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqNode
#define _defined_id_TpMeqNode 1
const DMI::TypeId TpMeqNode(-1378);               // from /home/oms/LOFAR/Timba/MEQ/src/Node.h:37
const int TpMeqNode_int = -1378;
namespace Meq { class Node; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Node> : public TypeTraits<Meq::Node>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqNode_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Node & ContainerReturnType;
                typedef const Meq::Node & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPolc
#define _defined_id_TpMeqPolc 1
const DMI::TypeId TpMeqPolc(-1361);               // from /home/oms/LOFAR/Timba/MEQ/src/Polc.h:32
const int TpMeqPolc_int = -1361;
namespace Meq { class Polc; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Polc> : public TypeTraits<Meq::Polc>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPolc_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Polc & ContainerReturnType;
                typedef const Meq::Polc & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPolcLog
#define _defined_id_TpMeqPolcLog 1
const DMI::TypeId TpMeqPolcLog(-1549);            // from /home/mevius/LOFAR/Timba/MEQ/src/PolcLog.h:9
const int TpMeqPolcLog_int = -1549;
namespace Meq { class PolcLog; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::PolcLog> : public TypeTraits<Meq::PolcLog>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPolcLog_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::PolcLog & ContainerReturnType;
                typedef const Meq::PolcLog & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqRequest
#define _defined_id_TpMeqRequest 1
const DMI::TypeId TpMeqRequest(-1357);            // from /home/oms/LOFAR/Timba/MEQ/src/Request.h:31
const int TpMeqRequest_int = -1357;
namespace Meq { class Request; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Request> : public TypeTraits<Meq::Request>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqRequest_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Request & ContainerReturnType;
                typedef const Meq::Request & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqResult
#define _defined_id_TpMeqResult 1
const DMI::TypeId TpMeqResult(-1360);             // from /home/oms/LOFAR/Timba/MEQ/src/Result.h:34
const int TpMeqResult_int = -1360;
namespace Meq { class Result; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Result> : public TypeTraits<Meq::Result>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqResult_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Result & ContainerReturnType;
                typedef const Meq::Result & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSpline
#define _defined_id_TpMeqSpline 1
const DMI::TypeId TpMeqSpline(-1704);             // from /home/mevius/Timba/MEQ/src/Spline.h:10
const int TpMeqSpline_int = -1704;
namespace Meq { class Spline; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Spline> : public TypeTraits<Meq::Spline>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSpline_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Spline & ContainerReturnType;
                typedef const Meq::Spline & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqVellSet
#define _defined_id_TpMeqVellSet 1
const DMI::TypeId TpMeqVellSet(-1307);            // from /home/oms/LOFAR/Timba/MEQ/src/VellSet.h:35
const int TpMeqVellSet_int = -1307;
namespace Meq { class VellSet; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::VellSet> : public TypeTraits<Meq::VellSet>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqVellSet_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::VellSet & ContainerReturnType;
                typedef const Meq::VellSet & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqVells
#define _defined_id_TpMeqVells 1
const DMI::TypeId TpMeqVells(-1341);              // from /home/oms/LOFAR/Timba/MEQ/src/Vells.h:30
const int TpMeqVells_int = -1341;
namespace Meq { class Vells; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Vells> : public TypeTraits<Meq::Vells>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqVells_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Vells & ContainerReturnType;
                typedef const Meq::Vells & ContainerParamType;
              };
            };
#endif


#endif
