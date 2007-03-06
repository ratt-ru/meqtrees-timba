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
