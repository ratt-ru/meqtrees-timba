      #ifndef TID_MeqMPI_h
      #define TID_MeqMPI_h 1
      
      // This file is generated automatically -- do not edit
      // Regenerate using "make aids"
      #include <DMI/TypeId.h>

      // should be called somewhere in order to link in the registry
      int aidRegistry_MeqMPI ();

#ifndef _defined_id_TpMeqMPIProxy
#define _defined_id_TpMeqMPIProxy 1
const DMI::TypeId TpMeqMPIProxy(-1739);           // from /home/oms/Timba/MeqMPI/src/MPIProxy.h:8
const int TpMeqMPIProxy_int = -1739;
namespace Meq { class MPIProxy; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::MPIProxy> : public TypeTraits<Meq::MPIProxy>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMPIProxy_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::MPIProxy & ContainerReturnType;
                typedef const Meq::MPIProxy & ContainerParamType;
              };
            };
#endif


#endif
