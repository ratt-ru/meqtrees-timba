      #ifndef TID_MeqNodes_h
      #define TID_MeqNodes_h 1
      
      // This file is generated automatically -- do not edit
      // Regenerate using "make aids"
      #include <DMI/TypeId.h>

      // should be called somewhere in order to link in the registry
      int aidRegistry_MeqNodes ();

#ifndef _defined_id_TpMeqAbs
#define _defined_id_TpMeqAbs 1
const DMI::TypeId TpMeqAbs(-1460);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Abs.h:29
const int TpMeqAbs_int = -1460;
namespace Meq { class Abs; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Abs> : public TypeTraits<Meq::Abs>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAbs_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Abs & ContainerReturnType;
                typedef const Meq::Abs & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAcos
#define _defined_id_TpMeqAcos 1
const DMI::TypeId TpMeqAcos(-1411);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Acos.h:29
const int TpMeqAcos_int = -1411;
namespace Meq { class Acos; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Acos> : public TypeTraits<Meq::Acos>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAcos_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Acos & ContainerReturnType;
                typedef const Meq::Acos & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAdd
#define _defined_id_TpMeqAdd 1
const DMI::TypeId TpMeqAdd(-1418);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Add.h:30
const int TpMeqAdd_int = -1418;
namespace Meq { class Add; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Add> : public TypeTraits<Meq::Add>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAdd_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Add & ContainerReturnType;
                typedef const Meq::Add & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqArg
#define _defined_id_TpMeqArg 1
const DMI::TypeId TpMeqArg(-1457);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Arg.h:29
const int TpMeqArg_int = -1457;
namespace Meq { class Arg; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Arg> : public TypeTraits<Meq::Arg>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqArg_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Arg & ContainerReturnType;
                typedef const Meq::Arg & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAsin
#define _defined_id_TpMeqAsin 1
const DMI::TypeId TpMeqAsin(-1399);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Asin.h:29
const int TpMeqAsin_int = -1399;
namespace Meq { class Asin; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Asin> : public TypeTraits<Meq::Asin>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAsin_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Asin & ContainerReturnType;
                typedef const Meq::Asin & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAtan
#define _defined_id_TpMeqAtan 1
const DMI::TypeId TpMeqAtan(-1428);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Atan.h:29
const int TpMeqAtan_int = -1428;
namespace Meq { class Atan; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Atan> : public TypeTraits<Meq::Atan>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAtan_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Atan & ContainerReturnType;
                typedef const Meq::Atan & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAtan2
#define _defined_id_TpMeqAtan2 1
const DMI::TypeId TpMeqAtan2(-1764);              // from src/Atan2.h:31
const int TpMeqAtan2_int = -1764;
namespace Meq { class Atan2; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Atan2> : public TypeTraits<Meq::Atan2>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAtan2_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Atan2 & ContainerReturnType;
                typedef const Meq::Atan2 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAzEl
#define _defined_id_TpMeqAzEl 1
const DMI::TypeId TpMeqAzEl(-1551);               // from /home/twillis/LOFAR/Timba/MeqNodes/src/AzEl.h:31
const int TpMeqAzEl_int = -1551;
namespace Meq { class AzEl; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::AzEl> : public TypeTraits<Meq::AzEl>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAzEl_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::AzEl & ContainerReturnType;
                typedef const Meq::AzEl & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqAzElRaDec
#define _defined_id_TpMeqAzElRaDec 1
const DMI::TypeId TpMeqAzElRaDec(-1763);          // from AzElRaDec.h:54
const int TpMeqAzElRaDec_int = -1763;
namespace Meq { class AzElRaDec; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::AzElRaDec> : public TypeTraits<Meq::AzElRaDec>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqAzElRaDec_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::AzElRaDec & ContainerReturnType;
                typedef const Meq::AzElRaDec & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqBessel
#define _defined_id_TpMeqBessel 1
const DMI::TypeId TpMeqBessel(-1734);             // from /home/sarod/Timba/MeqNodes/src/Bessel.h:32
const int TpMeqBessel_int = -1734;
namespace Meq { class Bessel; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Bessel> : public TypeTraits<Meq::Bessel>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqBessel_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Bessel & ContainerReturnType;
                typedef const Meq::Bessel & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCUDAPointSourceVisibility
#define _defined_id_TpMeqCUDAPointSourceVisibility 1
const DMI::TypeId TpMeqCUDAPointSourceVisibility(-1771);// from CUDAPointSourceVisibility.h:32
const int TpMeqCUDAPointSourceVisibility_int = -1771;
namespace Meq { class CUDAPointSourceVisibility; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::CUDAPointSourceVisibility> : public TypeTraits<Meq::CUDAPointSourceVisibility>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCUDAPointSourceVisibility_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::CUDAPointSourceVisibility & ContainerReturnType;
                typedef const Meq::CUDAPointSourceVisibility & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCeil
#define _defined_id_TpMeqCeil 1
const DMI::TypeId TpMeqCeil(-1437);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Ceil.h:30
const int TpMeqCeil_int = -1437;
namespace Meq { class Ceil; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Ceil> : public TypeTraits<Meq::Ceil>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCeil_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Ceil & ContainerReturnType;
                typedef const Meq::Ceil & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqComposer
#define _defined_id_TpMeqComposer 1
const DMI::TypeId TpMeqComposer(-1442);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Composer.h:30
const int TpMeqComposer_int = -1442;
namespace Meq { class Composer; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Composer> : public TypeTraits<Meq::Composer>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqComposer_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Composer & ContainerReturnType;
                typedef const Meq::Composer & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCompounder
#define _defined_id_TpMeqCompounder 1
const DMI::TypeId TpMeqCompounder(-1664);         // from /home/sarod/LOFAR/Timba/MeqNodes/src/Compounder.h:32
const int TpMeqCompounder_int = -1664;
namespace Meq { class Compounder; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Compounder> : public TypeTraits<Meq::Compounder>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCompounder_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Compounder & ContainerReturnType;
                typedef const Meq::Compounder & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCondeq
#define _defined_id_TpMeqCondeq 1
const DMI::TypeId TpMeqCondeq(-1443);             // from /home/oms/LOFAR/Timba/MeqNodes/src/Condeq.h:31
const int TpMeqCondeq_int = -1443;
namespace Meq { class Condeq; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Condeq> : public TypeTraits<Meq::Condeq>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCondeq_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Condeq & ContainerReturnType;
                typedef const Meq::Condeq & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqConj
#define _defined_id_TpMeqConj 1
const DMI::TypeId TpMeqConj(-1394);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Conj.h:30
const int TpMeqConj_int = -1394;
namespace Meq { class Conj; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Conj> : public TypeTraits<Meq::Conj>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqConj_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Conj & ContainerReturnType;
                typedef const Meq::Conj & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqConstant
#define _defined_id_TpMeqConstant 1
const DMI::TypeId TpMeqConstant(-1438);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Constant.h:34
const int TpMeqConstant_int = -1438;
namespace Meq { class Constant; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Constant> : public TypeTraits<Meq::Constant>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqConstant_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Constant & ContainerReturnType;
                typedef const Meq::Constant & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCoordTransform
#define _defined_id_TpMeqCoordTransform 1
const DMI::TypeId TpMeqCoordTransform(-1717);     // from /home/mevius/Timba/MeqNodes/src/CoordTransform.h:33
const int TpMeqCoordTransform_int = -1717;
namespace Meq { class CoordTransform; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::CoordTransform> : public TypeTraits<Meq::CoordTransform>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCoordTransform_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::CoordTransform & ContainerReturnType;
                typedef const Meq::CoordTransform & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCos
#define _defined_id_TpMeqCos 1
const DMI::TypeId TpMeqCos(-1398);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Cos.h:30
const int TpMeqCos_int = -1398;
namespace Meq { class Cos; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Cos> : public TypeTraits<Meq::Cos>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCos_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Cos & ContainerReturnType;
                typedef const Meq::Cos & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqCosh
#define _defined_id_TpMeqCosh 1
const DMI::TypeId TpMeqCosh(-1415);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Cosh.h:29
const int TpMeqCosh_int = -1415;
namespace Meq { class Cosh; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Cosh> : public TypeTraits<Meq::Cosh>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqCosh_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Cosh & ContainerReturnType;
                typedef const Meq::Cosh & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqDataCollect
#define _defined_id_TpMeqDataCollect 1
const DMI::TypeId TpMeqDataCollect(-1388);        // from /home/oms/LOFAR/Timba/MeqNodes/src/DataCollect.h:29
const int TpMeqDataCollect_int = -1388;
namespace Meq { class DataCollect; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::DataCollect> : public TypeTraits<Meq::DataCollect>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqDataCollect_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::DataCollect & ContainerReturnType;
                typedef const Meq::DataCollect & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqDataConcat
#define _defined_id_TpMeqDataConcat 1
const DMI::TypeId TpMeqDataConcat(-1448);         // from /home/oms/LOFAR/Timba/MeqNodes/src/DataConcat.h:30
const int TpMeqDataConcat_int = -1448;
namespace Meq { class DataConcat; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::DataConcat> : public TypeTraits<Meq::DataConcat>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqDataConcat_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::DataConcat & ContainerReturnType;
                typedef const Meq::DataConcat & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqDivide
#define _defined_id_TpMeqDivide 1
const DMI::TypeId TpMeqDivide(-1385);             // from /home/oms/LOFAR/Timba/MeqNodes/src/Divide.h:30
const int TpMeqDivide_int = -1385;
namespace Meq { class Divide; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Divide> : public TypeTraits<Meq::Divide>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqDivide_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Divide & ContainerReturnType;
                typedef const Meq::Divide & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqEMFPar
#define _defined_id_TpMeqEMFPar 1
const DMI::TypeId TpMeqEMFPar(-1762);             // from /home/oms/Timba/MeqNodes/src/EMFPar.h:54
const int TpMeqEMFPar_int = -1762;
namespace Meq { class EMFPar; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::EMFPar> : public TypeTraits<Meq::EMFPar>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqEMFPar_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::EMFPar & ContainerReturnType;
                typedef const Meq::EMFPar & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqExp
#define _defined_id_TpMeqExp 1
const DMI::TypeId TpMeqExp(-1393);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Exp.h:30
const int TpMeqExp_int = -1393;
namespace Meq { class Exp; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Exp> : public TypeTraits<Meq::Exp>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqExp_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Exp & ContainerReturnType;
                typedef const Meq::Exp & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFFTBrick
#define _defined_id_TpMeqFFTBrick 1
const DMI::TypeId TpMeqFFTBrick(-1570);           // from /home/rnijboer/LOFAR/Timba/MeqNodes/src/FFTBrick.h:34
const int TpMeqFFTBrick_int = -1570;
namespace Meq { class FFTBrick; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FFTBrick> : public TypeTraits<Meq::FFTBrick>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFFTBrick_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FFTBrick & ContainerReturnType;
                typedef const Meq::FFTBrick & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFITSDataMux
#define _defined_id_TpMeqFITSDataMux 1
const DMI::TypeId TpMeqFITSDataMux(-1690);        // from /home/sarod/LOFAR/Timba/MeqNodes/src/FITSDataMux.h:32
const int TpMeqFITSDataMux_int = -1690;
namespace Meq { class FITSDataMux; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FITSDataMux> : public TypeTraits<Meq::FITSDataMux>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFITSDataMux_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FITSDataMux & ContainerReturnType;
                typedef const Meq::FITSDataMux & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFITSImage
#define _defined_id_TpMeqFITSImage 1
const DMI::TypeId TpMeqFITSImage(-1653);          // from /home/sarod/LOFAR/Timba/MeqNodes/src/FITSImage.h:32
const int TpMeqFITSImage_int = -1653;
namespace Meq { class FITSImage; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FITSImage> : public TypeTraits<Meq::FITSImage>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFITSImage_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FITSImage & ContainerReturnType;
                typedef const Meq::FITSImage & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFITSReader
#define _defined_id_TpMeqFITSReader 1
const DMI::TypeId TpMeqFITSReader(-1677);         // from /home/sarod/LOFAR/Timba/MeqNodes/src/FITSReader.h:32
const int TpMeqFITSReader_int = -1677;
namespace Meq { class FITSReader; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FITSReader> : public TypeTraits<Meq::FITSReader>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFITSReader_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FITSReader & ContainerReturnType;
                typedef const Meq::FITSReader & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFITSSpigot
#define _defined_id_TpMeqFITSSpigot 1
const DMI::TypeId TpMeqFITSSpigot(-1689);         // from /home/sarod/LOFAR/Timba/MeqNodes/src/FITSSpigot.h:32
const int TpMeqFITSSpigot_int = -1689;
namespace Meq { class FITSSpigot; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FITSSpigot> : public TypeTraits<Meq::FITSSpigot>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFITSSpigot_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FITSSpigot & ContainerReturnType;
                typedef const Meq::FITSSpigot & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFITSWriter
#define _defined_id_TpMeqFITSWriter 1
const DMI::TypeId TpMeqFITSWriter(-1676);         // from /home/sarod/LOFAR/Timba/MeqNodes/src/FITSWriter.h:32
const int TpMeqFITSWriter_int = -1676;
namespace Meq { class FITSWriter; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FITSWriter> : public TypeTraits<Meq::FITSWriter>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFITSWriter_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FITSWriter & ContainerReturnType;
                typedef const Meq::FITSWriter & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFMod
#define _defined_id_TpMeqFMod 1
const DMI::TypeId TpMeqFMod(-1722);               // from /home/oms/Timba/MeqNodes/src/FMod.h:30
const int TpMeqFMod_int = -1722;
namespace Meq { class FMod; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::FMod> : public TypeTraits<Meq::FMod>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFMod_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::FMod & ContainerReturnType;
                typedef const Meq::FMod & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFabs
#define _defined_id_TpMeqFabs 1
const DMI::TypeId TpMeqFabs(-1429);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Fabs.h:29
const int TpMeqFabs_int = -1429;
namespace Meq { class Fabs; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Fabs> : public TypeTraits<Meq::Fabs>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFabs_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Fabs & ContainerReturnType;
                typedef const Meq::Fabs & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFloor
#define _defined_id_TpMeqFloor 1
const DMI::TypeId TpMeqFloor(-1436);              // from /home/oms/LOFAR/Timba/MeqNodes/src/Floor.h:30
const int TpMeqFloor_int = -1436;
namespace Meq { class Floor; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Floor> : public TypeTraits<Meq::Floor>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFloor_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Floor & ContainerReturnType;
                typedef const Meq::Floor & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFreq
#define _defined_id_TpMeqFreq 1
const DMI::TypeId TpMeqFreq(-1420);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Freq.h:30
const int TpMeqFreq_int = -1420;
namespace Meq { class Freq; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Freq> : public TypeTraits<Meq::Freq>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFreq_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Freq & ContainerReturnType;
                typedef const Meq::Freq & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqFunctional
#define _defined_id_TpMeqFunctional 1
const DMI::TypeId TpMeqFunctional(-1673);         // from /home/mevius/LOFAR/Timba/MeqNodes/src/Functional.h:33
const int TpMeqFunctional_int = -1673;
namespace Meq { class Functional; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Functional> : public TypeTraits<Meq::Functional>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqFunctional_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Functional & ContainerReturnType;
                typedef const Meq::Functional & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqGaussNoise
#define _defined_id_TpMeqGaussNoise 1
const DMI::TypeId TpMeqGaussNoise(-1449);         // from /home/oms/LOFAR/Timba/MeqNodes/src/GaussNoise.h:31
const int TpMeqGaussNoise_int = -1449;
namespace Meq { class GaussNoise; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::GaussNoise> : public TypeTraits<Meq::GaussNoise>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqGaussNoise_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::GaussNoise & ContainerReturnType;
                typedef const Meq::GaussNoise & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqGrid
#define _defined_id_TpMeqGrid 1
const DMI::TypeId TpMeqGrid(-1681);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Grid.h:30
const int TpMeqGrid_int = -1681;
namespace Meq { class Grid; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Grid> : public TypeTraits<Meq::Grid>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqGrid_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Grid & ContainerReturnType;
                typedef const Meq::Grid & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqGridPoints
#define _defined_id_TpMeqGridPoints 1
const DMI::TypeId TpMeqGridPoints(-1666);         // from /home/oms/LOFAR/Timba/MeqNodes/src/GridPoints.h:30
const int TpMeqGridPoints_int = -1666;
namespace Meq { class GridPoints; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::GridPoints> : public TypeTraits<Meq::GridPoints>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqGridPoints_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::GridPoints & ContainerReturnType;
                typedef const Meq::GridPoints & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqHistoryCollect
#define _defined_id_TpMeqHistoryCollect 1
const DMI::TypeId TpMeqHistoryCollect(-1574);     // from /home/oms/LOFAR/Timba/MeqNodes/src/HistoryCollect.h:29
const int TpMeqHistoryCollect_int = -1574;
namespace Meq { class HistoryCollect; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::HistoryCollect> : public TypeTraits<Meq::HistoryCollect>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqHistoryCollect_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::HistoryCollect & ContainerReturnType;
                typedef const Meq::HistoryCollect & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqIdentity
#define _defined_id_TpMeqIdentity 1
const DMI::TypeId TpMeqIdentity(-1678);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Identity.h:31
const int TpMeqIdentity_int = -1678;
namespace Meq { class Identity; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Identity> : public TypeTraits<Meq::Identity>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqIdentity_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Identity & ContainerReturnType;
                typedef const Meq::Identity & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqImag
#define _defined_id_TpMeqImag 1
const DMI::TypeId TpMeqImag(-1427);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Imag.h:29
const int TpMeqImag_int = -1427;
namespace Meq { class Imag; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Imag> : public TypeTraits<Meq::Imag>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqImag_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Imag & ContainerReturnType;
                typedef const Meq::Imag & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqInterpolCoeff
#define _defined_id_TpMeqInterpolCoeff 1
const DMI::TypeId TpMeqInterpolCoeff(-1752);      // from /home/fba/Timba/MeqNodes/src/InterpolCoeff.h:36
const int TpMeqInterpolCoeff_int = -1752;
namespace Meq { class InterpolCoeff; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::InterpolCoeff> : public TypeTraits<Meq::InterpolCoeff>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqInterpolCoeff_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::InterpolCoeff & ContainerReturnType;
                typedef const Meq::InterpolCoeff & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqInvert
#define _defined_id_TpMeqInvert 1
const DMI::TypeId TpMeqInvert(-1507);             // from /home/assendorp/LOFAR/Timba/MeqNodes/src/Invert.h:29
const int TpMeqInvert_int = -1507;
namespace Meq { class Invert; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Invert> : public TypeTraits<Meq::Invert>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqInvert_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Invert & ContainerReturnType;
                typedef const Meq::Invert & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqLMN
#define _defined_id_TpMeqLMN 1
const DMI::TypeId TpMeqLMN(-1410);                // from /home/oms/LOFAR/Timba/MeqNodes/src/LMN.h:30
const int TpMeqLMN_int = -1410;
namespace Meq { class LMN; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::LMN> : public TypeTraits<Meq::LMN>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqLMN_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::LMN & ContainerReturnType;
                typedef const Meq::LMN & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqLMRaDec
#define _defined_id_TpMeqLMRaDec 1
const DMI::TypeId TpMeqLMRaDec(-1696);            // from /home/twillis/Timba/MeqNodes/src/LMRaDec.h:29
const int TpMeqLMRaDec_int = -1696;
namespace Meq { class LMRaDec; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::LMRaDec> : public TypeTraits<Meq::LMRaDec>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqLMRaDec_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::LMRaDec & ContainerReturnType;
                typedef const Meq::LMRaDec & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqLST
#define _defined_id_TpMeqLST 1
const DMI::TypeId TpMeqLST(-1726);                // from /home/twillis/Timba/MeqNodes/src/LST.h:49
const int TpMeqLST_int = -1726;
namespace Meq { class LST; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::LST> : public TypeTraits<Meq::LST>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqLST_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::LST & ContainerReturnType;
                typedef const Meq::LST & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqLog
#define _defined_id_TpMeqLog 1
const DMI::TypeId TpMeqLog(-1397);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Log.h:29
const int TpMeqLog_int = -1397;
namespace Meq { class Log; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Log> : public TypeTraits<Meq::Log>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqLog_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Log & ContainerReturnType;
                typedef const Meq::Log & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqLongLat
#define _defined_id_TpMeqLongLat 1
const DMI::TypeId TpMeqLongLat(-1732);            // from /home/mevius/Timba/MeqNodes/src/LongLat.h:30
const int TpMeqLongLat_int = -1732;
namespace Meq { class LongLat; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::LongLat> : public TypeTraits<Meq::LongLat>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqLongLat_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::LongLat & ContainerReturnType;
                typedef const Meq::LongLat & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMatrixInvert22
#define _defined_id_TpMeqMatrixInvert22 1
const DMI::TypeId TpMeqMatrixInvert22(-1522);     // from /home/oms/LOFAR/Timba/MeqNodes/src/MatrixInvert22.h:30
const int TpMeqMatrixInvert22_int = -1522;
namespace Meq { class MatrixInvert22; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::MatrixInvert22> : public TypeTraits<Meq::MatrixInvert22>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMatrixInvert22_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::MatrixInvert22 & ContainerReturnType;
                typedef const Meq::MatrixInvert22 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMatrixMultiply
#define _defined_id_TpMeqMatrixMultiply 1
const DMI::TypeId TpMeqMatrixMultiply(-1516);     // from /home/oms/LOFAR/Timba/MeqNodes/src/MatrixMultiply.h:30
const int TpMeqMatrixMultiply_int = -1516;
namespace Meq { class MatrixMultiply; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::MatrixMultiply> : public TypeTraits<Meq::MatrixMultiply>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMatrixMultiply_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::MatrixMultiply & ContainerReturnType;
                typedef const Meq::MatrixMultiply & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMax
#define _defined_id_TpMeqMax 1
const DMI::TypeId TpMeqMax(-1452);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Max.h:29
const int TpMeqMax_int = -1452;
namespace Meq { class Max; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Max> : public TypeTraits<Meq::Max>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMax_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Max & ContainerReturnType;
                typedef const Meq::Max & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMaxLocation
#define _defined_id_TpMeqMaxLocation 1
const DMI::TypeId TpMeqMaxLocation(-1699);        // from /home/sarod/Timba/MeqNodes/src/MaxLocation.h:30
const int TpMeqMaxLocation_int = -1699;
namespace Meq { class MaxLocation; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::MaxLocation> : public TypeTraits<Meq::MaxLocation>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMaxLocation_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::MaxLocation & ContainerReturnType;
                typedef const Meq::MaxLocation & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMean
#define _defined_id_TpMeqMean 1
const DMI::TypeId TpMeqMean(-1416);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Mean.h:29
const int TpMeqMean_int = -1416;
namespace Meq { class Mean; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Mean> : public TypeTraits<Meq::Mean>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMean_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Mean & ContainerReturnType;
                typedef const Meq::Mean & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMergeFlags
#define _defined_id_TpMeqMergeFlags 1
const DMI::TypeId TpMeqMergeFlags(-1441);         // from /home/oms/LOFAR/Timba/MeqNodes/src/MergeFlags.h:31
const int TpMeqMergeFlags_int = -1441;
namespace Meq { class MergeFlags; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::MergeFlags> : public TypeTraits<Meq::MergeFlags>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMergeFlags_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::MergeFlags & ContainerReturnType;
                typedef const Meq::MergeFlags & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMin
#define _defined_id_TpMeqMin 1
const DMI::TypeId TpMeqMin(-1392);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Min.h:29
const int TpMeqMin_int = -1392;
namespace Meq { class Min; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Min> : public TypeTraits<Meq::Min>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMin_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Min & ContainerReturnType;
                typedef const Meq::Min & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMinLocation
#define _defined_id_TpMeqMinLocation 1
const DMI::TypeId TpMeqMinLocation(-1700);        // from /home/sarod/Timba/MeqNodes/src/MinLocation.h:30
const int TpMeqMinLocation_int = -1700;
namespace Meq { class MinLocation; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::MinLocation> : public TypeTraits<Meq::MinLocation>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMinLocation_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::MinLocation & ContainerReturnType;
                typedef const Meq::MinLocation & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqModRes
#define _defined_id_TpMeqModRes 1
const DMI::TypeId TpMeqModRes(-1592);             // from /home/sarod/LOFAR/Timba/MeqNodes/src/ModRes.h:32
const int TpMeqModRes_int = -1592;
namespace Meq { class ModRes; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ModRes> : public TypeTraits<Meq::ModRes>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqModRes_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ModRes & ContainerReturnType;
                typedef const Meq::ModRes & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqMultiply
#define _defined_id_TpMeqMultiply 1
const DMI::TypeId TpMeqMultiply(-1391);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Multiply.h:30
const int TpMeqMultiply_int = -1391;
namespace Meq { class Multiply; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Multiply> : public TypeTraits<Meq::Multiply>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqMultiply_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Multiply & ContainerReturnType;
                typedef const Meq::Multiply & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqNBrick
#define _defined_id_TpMeqNBrick 1
const DMI::TypeId TpMeqNBrick(-1785);             // from NBrick.h:34
const int TpMeqNBrick_int = -1785;
namespace Meq { class NBrick; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::NBrick> : public TypeTraits<Meq::NBrick>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqNBrick_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::NBrick & ContainerReturnType;
                typedef const Meq::NBrick & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqNElements
#define _defined_id_TpMeqNElements 1
const DMI::TypeId TpMeqNElements(-1500);          // from /home/oms/LOFAR/Timba/MeqNodes/src/NElements.h:29
const int TpMeqNElements_int = -1500;
namespace Meq { class NElements; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::NElements> : public TypeTraits<Meq::NElements>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqNElements_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::NElements & ContainerReturnType;
                typedef const Meq::NElements & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqNegate
#define _defined_id_TpMeqNegate 1
const DMI::TypeId TpMeqNegate(-1506);             // from /home/assendorp/LOFAR/Timba/MeqNodes/src/Negate.h:29
const int TpMeqNegate_int = -1506;
namespace Meq { class Negate; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Negate> : public TypeTraits<Meq::Negate>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqNegate_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Negate & ContainerReturnType;
                typedef const Meq::Negate & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqNorm
#define _defined_id_TpMeqNorm 1
const DMI::TypeId TpMeqNorm(-1459);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Norm.h:29
const int TpMeqNorm_int = -1459;
namespace Meq { class Norm; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Norm> : public TypeTraits<Meq::Norm>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqNorm_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Norm & ContainerReturnType;
                typedef const Meq::Norm & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqObjectRADec
#define _defined_id_TpMeqObjectRADec 1
const DMI::TypeId TpMeqObjectRADec(-1716);        // from /home/sarod/Timba/MeqNodes/src/ObjectRADec.h:30
const int TpMeqObjectRADec_int = -1716;
namespace Meq { class ObjectRADec; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ObjectRADec> : public TypeTraits<Meq::ObjectRADec>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqObjectRADec_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ObjectRADec & ContainerReturnType;
                typedef const Meq::ObjectRADec & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPSVTensor
#define _defined_id_TpMeqPSVTensor 1
const DMI::TypeId TpMeqPSVTensor(-1772);          // from PSVTensor.h:32
const int TpMeqPSVTensor_int = -1772;
namespace Meq { class PSVTensor; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::PSVTensor> : public TypeTraits<Meq::PSVTensor>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPSVTensor_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::PSVTensor & ContainerReturnType;
                typedef const Meq::PSVTensor & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqParAngle
#define _defined_id_TpMeqParAngle 1
const DMI::TypeId TpMeqParAngle(-1695);           // from /home/twillis/Timba/MeqNodes/src/ParAngle.h:40
const int TpMeqParAngle_int = -1695;
namespace Meq { class ParAngle; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ParAngle> : public TypeTraits<Meq::ParAngle>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqParAngle_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ParAngle & ContainerReturnType;
                typedef const Meq::ParAngle & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqParm
#define _defined_id_TpMeqParm 1
const DMI::TypeId TpMeqParm(-1454);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Parm.h:35
const int TpMeqParm_int = -1454;
namespace Meq { class Parm; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Parm> : public TypeTraits<Meq::Parm>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqParm_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Parm & ContainerReturnType;
                typedef const Meq::Parm & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPaster
#define _defined_id_TpMeqPaster 1
const DMI::TypeId TpMeqPaster(-1519);             // from /home/oms/LOFAR/Timba/MeqNodes/src/Paster.h:31
const int TpMeqPaster_int = -1519;
namespace Meq { class Paster; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Paster> : public TypeTraits<Meq::Paster>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPaster_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Paster & ContainerReturnType;
                typedef const Meq::Paster & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPatchComposer
#define _defined_id_TpMeqPatchComposer 1
const DMI::TypeId TpMeqPatchComposer(-1569);      // from /home/rnijboer/LOFAR/Timba/MeqNodes/src/PatchComposer.h:34
const int TpMeqPatchComposer_int = -1569;
namespace Meq { class PatchComposer; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::PatchComposer> : public TypeTraits<Meq::PatchComposer>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPatchComposer_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::PatchComposer & ContainerReturnType;
                typedef const Meq::PatchComposer & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPolar
#define _defined_id_TpMeqPolar 1
const DMI::TypeId TpMeqPolar(-1383);              // from /home/oms/LOFAR/Timba/MeqNodes/src/Polar.h:30
const int TpMeqPolar_int = -1383;
namespace Meq { class Polar; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Polar> : public TypeTraits<Meq::Polar>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPolar_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Polar & ContainerReturnType;
                typedef const Meq::Polar & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow
#define _defined_id_TpMeqPow 1
const DMI::TypeId TpMeqPow(-1386);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow.h:30
const int TpMeqPow_int = -1386;
namespace Meq { class Pow; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow> : public TypeTraits<Meq::Pow>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow & ContainerReturnType;
                typedef const Meq::Pow & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow2
#define _defined_id_TpMeqPow2 1
const DMI::TypeId TpMeqPow2(-1439);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow2.h:29
const int TpMeqPow2_int = -1439;
namespace Meq { class Pow2; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow2> : public TypeTraits<Meq::Pow2>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow2_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow2 & ContainerReturnType;
                typedef const Meq::Pow2 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow3
#define _defined_id_TpMeqPow3 1
const DMI::TypeId TpMeqPow3(-1412);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow3.h:29
const int TpMeqPow3_int = -1412;
namespace Meq { class Pow3; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow3> : public TypeTraits<Meq::Pow3>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow3_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow3 & ContainerReturnType;
                typedef const Meq::Pow3 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow4
#define _defined_id_TpMeqPow4 1
const DMI::TypeId TpMeqPow4(-1403);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow4.h:29
const int TpMeqPow4_int = -1403;
namespace Meq { class Pow4; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow4> : public TypeTraits<Meq::Pow4>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow4_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow4 & ContainerReturnType;
                typedef const Meq::Pow4 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow5
#define _defined_id_TpMeqPow5 1
const DMI::TypeId TpMeqPow5(-1422);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow5.h:29
const int TpMeqPow5_int = -1422;
namespace Meq { class Pow5; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow5> : public TypeTraits<Meq::Pow5>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow5_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow5 & ContainerReturnType;
                typedef const Meq::Pow5 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow6
#define _defined_id_TpMeqPow6 1
const DMI::TypeId TpMeqPow6(-1445);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow6.h:29
const int TpMeqPow6_int = -1445;
namespace Meq { class Pow6; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow6> : public TypeTraits<Meq::Pow6>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow6_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow6 & ContainerReturnType;
                typedef const Meq::Pow6 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow7
#define _defined_id_TpMeqPow7 1
const DMI::TypeId TpMeqPow7(-1387);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow7.h:29
const int TpMeqPow7_int = -1387;
namespace Meq { class Pow7; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow7> : public TypeTraits<Meq::Pow7>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow7_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow7 & ContainerReturnType;
                typedef const Meq::Pow7 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPow8
#define _defined_id_TpMeqPow8 1
const DMI::TypeId TpMeqPow8(-1395);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Pow8.h:29
const int TpMeqPow8_int = -1395;
namespace Meq { class Pow8; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Pow8> : public TypeTraits<Meq::Pow8>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPow8_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Pow8 & ContainerReturnType;
                typedef const Meq::Pow8 & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqPrivateFunction
#define _defined_id_TpMeqPrivateFunction 1
const DMI::TypeId TpMeqPrivateFunction(-1692);    // from /home/mevius/LOFAR/Timba/MeqNodes/src/PrivateFunction.h:30
const int TpMeqPrivateFunction_int = -1692;
namespace Meq { class PrivateFunction; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::PrivateFunction> : public TypeTraits<Meq::PrivateFunction>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqPrivateFunction_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::PrivateFunction & ContainerReturnType;
                typedef const Meq::PrivateFunction & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqProduct
#define _defined_id_TpMeqProduct 1
const DMI::TypeId TpMeqProduct(-1501);            // from /home/oms/LOFAR/Timba/MeqNodes/src/Product.h:29
const int TpMeqProduct_int = -1501;
namespace Meq { class Product; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Product> : public TypeTraits<Meq::Product>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqProduct_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Product & ContainerReturnType;
                typedef const Meq::Product & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqRADec
#define _defined_id_TpMeqRADec 1
const DMI::TypeId TpMeqRADec(-1709);              // from /home/sarod/Timba/MeqNodes/src/RADec.h:52
const int TpMeqRADec_int = -1709;
namespace Meq { class RADec; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::RADec> : public TypeTraits<Meq::RADec>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqRADec_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::RADec & ContainerReturnType;
                typedef const Meq::RADec & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqRandomNoise
#define _defined_id_TpMeqRandomNoise 1
const DMI::TypeId TpMeqRandomNoise(-1384);        // from /home/oms/LOFAR/Timba/MeqNodes/src/RandomNoise.h:31
const int TpMeqRandomNoise_int = -1384;
namespace Meq { class RandomNoise; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::RandomNoise> : public TypeTraits<Meq::RandomNoise>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqRandomNoise_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::RandomNoise & ContainerReturnType;
                typedef const Meq::RandomNoise & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqReal
#define _defined_id_TpMeqReal 1
const DMI::TypeId TpMeqReal(-1404);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Real.h:29
const int TpMeqReal_int = -1404;
namespace Meq { class Real; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Real> : public TypeTraits<Meq::Real>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqReal_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Real & ContainerReturnType;
                typedef const Meq::Real & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqReplaceFlaggedValues
#define _defined_id_TpMeqReplaceFlaggedValues 1
const DMI::TypeId TpMeqReplaceFlaggedValues(-1776);// from ReplaceFlaggedValues.h:31
const int TpMeqReplaceFlaggedValues_int = -1776;
namespace Meq { class ReplaceFlaggedValues; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ReplaceFlaggedValues> : public TypeTraits<Meq::ReplaceFlaggedValues>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqReplaceFlaggedValues_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ReplaceFlaggedValues & ContainerReturnType;
                typedef const Meq::ReplaceFlaggedValues & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqReqMux
#define _defined_id_TpMeqReqMux 1
const DMI::TypeId TpMeqReqMux(-1608);             // from /home/oms/LOFAR/Timba/MeqNodes/src/ReqMux.h:31
const int TpMeqReqMux_int = -1608;
namespace Meq { class ReqMux; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ReqMux> : public TypeTraits<Meq::ReqMux>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqReqMux_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ReqMux & ContainerReturnType;
                typedef const Meq::ReqMux & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqReqSeq
#define _defined_id_TpMeqReqSeq 1
const DMI::TypeId TpMeqReqSeq(-1425);             // from /home/oms/LOFAR/Timba/MeqNodes/src/ReqSeq.h:31
const int TpMeqReqSeq_int = -1425;
namespace Meq { class ReqSeq; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ReqSeq> : public TypeTraits<Meq::ReqSeq>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqReqSeq_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ReqSeq & ContainerReturnType;
                typedef const Meq::ReqSeq & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqResampler
#define _defined_id_TpMeqResampler 1
const DMI::TypeId TpMeqResampler(-1591);          // from /home/sarod/LOFAR/Timba/MeqNodes/src/Resampler.h:31
const int TpMeqResampler_int = -1591;
namespace Meq { class Resampler; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Resampler> : public TypeTraits<Meq::Resampler>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqResampler_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Resampler & ContainerReturnType;
                typedef const Meq::Resampler & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqRms
#define _defined_id_TpMeqRms 1
const DMI::TypeId TpMeqRms(-1718);                // from /home/oms/Timba/MeqNodes/src/Rms.h:29
const int TpMeqRms_int = -1718;
namespace Meq { class Rms; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Rms> : public TypeTraits<Meq::Rms>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqRms_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Rms & ContainerReturnType;
                typedef const Meq::Rms & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSelector
#define _defined_id_TpMeqSelector 1
const DMI::TypeId TpMeqSelector(-1447);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Selector.h:30
const int TpMeqSelector_int = -1447;
namespace Meq { class Selector; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Selector> : public TypeTraits<Meq::Selector>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSelector_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Selector & ContainerReturnType;
                typedef const Meq::Selector & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqShapeletVisTf
#define _defined_id_TpMeqShapeletVisTf 1
const DMI::TypeId TpMeqShapeletVisTf(-1694);      // from /home/sarod/LOFAR/Timba/MeqNodes/src/ShapeletVisTf.h:32
const int TpMeqShapeletVisTf_int = -1694;
namespace Meq { class ShapeletVisTf; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ShapeletVisTf> : public TypeTraits<Meq::ShapeletVisTf>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqShapeletVisTf_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ShapeletVisTf & ContainerReturnType;
                typedef const Meq::ShapeletVisTf & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSin
#define _defined_id_TpMeqSin 1
const DMI::TypeId TpMeqSin(-1430);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Sin.h:30
const int TpMeqSin_int = -1430;
namespace Meq { class Sin; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Sin> : public TypeTraits<Meq::Sin>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSin_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Sin & ContainerReturnType;
                typedef const Meq::Sin & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSinh
#define _defined_id_TpMeqSinh 1
const DMI::TypeId TpMeqSinh(-1407);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Sinh.h:29
const int TpMeqSinh_int = -1407;
namespace Meq { class Sinh; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Sinh> : public TypeTraits<Meq::Sinh>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSinh_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Sinh & ContainerReturnType;
                typedef const Meq::Sinh & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSolver
#define _defined_id_TpMeqSolver 1
const DMI::TypeId TpMeqSolver(-1401);             // from /home/oms/LOFAR/Timba/MeqNodes/src/Solver.h:30
const int TpMeqSolver_int = -1401;
namespace Meq { class Solver; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Solver> : public TypeTraits<Meq::Solver>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSolver_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Solver & ContainerReturnType;
                typedef const Meq::Solver & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSqr
#define _defined_id_TpMeqSqr 1
const DMI::TypeId TpMeqSqr(-1458);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Sqr.h:30
const int TpMeqSqr_int = -1458;
namespace Meq { class Sqr; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Sqr> : public TypeTraits<Meq::Sqr>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSqr_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Sqr & ContainerReturnType;
                typedef const Meq::Sqr & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSqrt
#define _defined_id_TpMeqSqrt 1
const DMI::TypeId TpMeqSqrt(-1408);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Sqrt.h:30
const int TpMeqSqrt_int = -1408;
namespace Meq { class Sqrt; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Sqrt> : public TypeTraits<Meq::Sqrt>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSqrt_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Sqrt & ContainerReturnType;
                typedef const Meq::Sqrt & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqStationBeam
#define _defined_id_TpMeqStationBeam 1
const DMI::TypeId TpMeqStationBeam(-1727);        // from /home/sarod/Timba/MeqNodes/src/StationBeam.h:33
const int TpMeqStationBeam_int = -1727;
namespace Meq { class StationBeam; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::StationBeam> : public TypeTraits<Meq::StationBeam>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqStationBeam_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::StationBeam & ContainerReturnType;
                typedef const Meq::StationBeam & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqStdDev
#define _defined_id_TpMeqStdDev 1
const DMI::TypeId TpMeqStdDev(-1491);             // from /home/oms/LOFAR/Timba/MeqNodes/src/StdDev.h:29
const int TpMeqStdDev_int = -1491;
namespace Meq { class StdDev; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::StdDev> : public TypeTraits<Meq::StdDev>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqStdDev_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::StdDev & ContainerReturnType;
                typedef const Meq::StdDev & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqStokes
#define _defined_id_TpMeqStokes 1
const DMI::TypeId TpMeqStokes(-1568);             // from /home/rnijboer/LOFAR/Timba/MeqNodes/src/Stokes.h:34
const int TpMeqStokes_int = -1568;
namespace Meq { class Stokes; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Stokes> : public TypeTraits<Meq::Stokes>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqStokes_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Stokes & ContainerReturnType;
                typedef const Meq::Stokes & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqStripper
#define _defined_id_TpMeqStripper 1
const DMI::TypeId TpMeqStripper(-1409);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Stripper.h:30
const int TpMeqStripper_int = -1409;
namespace Meq { class Stripper; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Stripper> : public TypeTraits<Meq::Stripper>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqStripper_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Stripper & ContainerReturnType;
                typedef const Meq::Stripper & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSubtract
#define _defined_id_TpMeqSubtract 1
const DMI::TypeId TpMeqSubtract(-1461);           // from /home/oms/LOFAR/Timba/MeqNodes/src/Subtract.h:30
const int TpMeqSubtract_int = -1461;
namespace Meq { class Subtract; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Subtract> : public TypeTraits<Meq::Subtract>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSubtract_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Subtract & ContainerReturnType;
                typedef const Meq::Subtract & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqSum
#define _defined_id_TpMeqSum 1
const DMI::TypeId TpMeqSum(-1499);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Sum.h:29
const int TpMeqSum_int = -1499;
namespace Meq { class Sum; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Sum> : public TypeTraits<Meq::Sum>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqSum_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Sum & ContainerReturnType;
                typedef const Meq::Sum & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqTFSmearFactor
#define _defined_id_TpMeqTFSmearFactor 1
const DMI::TypeId TpMeqTFSmearFactor(-1748);      // from /home/oms/Timba/MeqNodes/src/TFSmear.h:31
const int TpMeqTFSmearFactor_int = -1748;
namespace Meq { class TFSmearFactor; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::TFSmearFactor> : public TypeTraits<Meq::TFSmearFactor>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqTFSmearFactor_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::TFSmearFactor & ContainerReturnType;
                typedef const Meq::TFSmearFactor & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqTFSmearFactorApprox
#define _defined_id_TpMeqTFSmearFactorApprox 1
const DMI::TypeId TpMeqTFSmearFactorApprox(-1766);// from TFSmearFactorApprox.h:32
const int TpMeqTFSmearFactorApprox_int = -1766;
namespace Meq { class TFSmearFactorApprox; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::TFSmearFactorApprox> : public TypeTraits<Meq::TFSmearFactorApprox>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqTFSmearFactorApprox_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::TFSmearFactorApprox & ContainerReturnType;
                typedef const Meq::TFSmearFactorApprox & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqTan
#define _defined_id_TpMeqTan 1
const DMI::TypeId TpMeqTan(-1417);                // from /home/oms/LOFAR/Timba/MeqNodes/src/Tan.h:29
const int TpMeqTan_int = -1417;
namespace Meq { class Tan; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Tan> : public TypeTraits<Meq::Tan>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqTan_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Tan & ContainerReturnType;
                typedef const Meq::Tan & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqTanh
#define _defined_id_TpMeqTanh 1
const DMI::TypeId TpMeqTanh(-1450);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Tanh.h:29
const int TpMeqTanh_int = -1450;
namespace Meq { class Tanh; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Tanh> : public TypeTraits<Meq::Tanh>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqTanh_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Tanh & ContainerReturnType;
                typedef const Meq::Tanh & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqThrustPointSourceVisibility
#define _defined_id_TpMeqThrustPointSourceVisibility 1
const DMI::TypeId TpMeqThrustPointSourceVisibility(-1781);// from ThrustPointSourceVisibility.h:33
const int TpMeqThrustPointSourceVisibility_int = -1781;
namespace Meq { class ThrustPointSourceVisibility; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ThrustPointSourceVisibility> : public TypeTraits<Meq::ThrustPointSourceVisibility>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqThrustPointSourceVisibility_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ThrustPointSourceVisibility & ContainerReturnType;
                typedef const Meq::ThrustPointSourceVisibility & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqTime
#define _defined_id_TpMeqTime 1
const DMI::TypeId TpMeqTime(-1451);               // from /home/oms/LOFAR/Timba/MeqNodes/src/Time.h:30
const int TpMeqTime_int = -1451;
namespace Meq { class Time; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Time> : public TypeTraits<Meq::Time>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqTime_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Time & ContainerReturnType;
                typedef const Meq::Time & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqToComplex
#define _defined_id_TpMeqToComplex 1
const DMI::TypeId TpMeqToComplex(-1413);          // from /home/oms/LOFAR/Timba/MeqNodes/src/ToComplex.h:30
const int TpMeqToComplex_int = -1413;
namespace Meq { class ToComplex; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ToComplex> : public TypeTraits<Meq::ToComplex>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqToComplex_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ToComplex & ContainerReturnType;
                typedef const Meq::ToComplex & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqTranspose
#define _defined_id_TpMeqTranspose 1
const DMI::TypeId TpMeqTranspose(-1521);          // from /home/oms/LOFAR/Timba/MeqNodes/src/Transpose.h:31
const int TpMeqTranspose_int = -1521;
namespace Meq { class Transpose; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::Transpose> : public TypeTraits<Meq::Transpose>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqTranspose_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::Transpose & ContainerReturnType;
                typedef const Meq::Transpose & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqUVBrick
#define _defined_id_TpMeqUVBrick 1
const DMI::TypeId TpMeqUVBrick(-1505);            // from /home/mevius/LOFAR/Timba/MeqNodes/src/UVBrick.h:31
const int TpMeqUVBrick_int = -1505;
namespace Meq { class UVBrick; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::UVBrick> : public TypeTraits<Meq::UVBrick>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqUVBrick_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::UVBrick & ContainerReturnType;
                typedef const Meq::UVBrick & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqUVDetaper
#define _defined_id_TpMeqUVDetaper 1
const DMI::TypeId TpMeqUVDetaper(-1758);          // from /home/fba/Timba/MeqNodes/src/UVDetaper.h:31
const int TpMeqUVDetaper_int = -1758;
namespace Meq { class UVDetaper; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::UVDetaper> : public TypeTraits<Meq::UVDetaper>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqUVDetaper_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::UVDetaper & ContainerReturnType;
                typedef const Meq::UVDetaper & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqUVInterpol
#define _defined_id_TpMeqUVInterpol 1
const DMI::TypeId TpMeqUVInterpol(-1508);         // from /home/rnijboer/LOFAR/Timba/MeqNodes/src/UVInterpol.h:33
const int TpMeqUVInterpol_int = -1508;
namespace Meq { class UVInterpol; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::UVInterpol> : public TypeTraits<Meq::UVInterpol>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqUVInterpol_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::UVInterpol & ContainerReturnType;
                typedef const Meq::UVInterpol & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqUVInterpolWave
#define _defined_id_TpMeqUVInterpolWave 1
const DMI::TypeId TpMeqUVInterpolWave(-1688);     // from /home/rnijboer/LOFAR/Timba/MeqNodes/src/UVInterpolWave.h:35
const int TpMeqUVInterpolWave_int = -1688;
namespace Meq { class UVInterpolWave; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::UVInterpolWave> : public TypeTraits<Meq::UVInterpolWave>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqUVInterpolWave_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::UVInterpolWave & ContainerReturnType;
                typedef const Meq::UVInterpolWave & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqUVW
#define _defined_id_TpMeqUVW 1
const DMI::TypeId TpMeqUVW(-1421);                // from /home/oms/LOFAR/Timba/MeqNodes/src/UVW.h:31
const int TpMeqUVW_int = -1421;
namespace Meq { class UVW; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::UVW> : public TypeTraits<Meq::UVW>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqUVW_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::UVW & ContainerReturnType;
                typedef const Meq::UVW & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqVisPhaseShift
#define _defined_id_TpMeqVisPhaseShift 1
const DMI::TypeId TpMeqVisPhaseShift(-1517);      // from /home/brentjens/LOFAR/Timba/MeqNodes/src/VisPhaseShift.h:31
const int TpMeqVisPhaseShift_int = -1517;
namespace Meq { class VisPhaseShift; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::VisPhaseShift> : public TypeTraits<Meq::VisPhaseShift>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqVisPhaseShift_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::VisPhaseShift & ContainerReturnType;
                typedef const Meq::VisPhaseShift & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqVisPhaseShiftArg
#define _defined_id_TpMeqVisPhaseShiftArg 1
const DMI::TypeId TpMeqVisPhaseShiftArg(-1747);   // from /home/oms/Timba/MeqNodes/src/VisPhaseShiftArg.h:32
const int TpMeqVisPhaseShiftArg_int = -1747;
namespace Meq { class VisPhaseShiftArg; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::VisPhaseShiftArg> : public TypeTraits<Meq::VisPhaseShiftArg>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqVisPhaseShiftArg_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::VisPhaseShiftArg & ContainerReturnType;
                typedef const Meq::VisPhaseShiftArg & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqWMean
#define _defined_id_TpMeqWMean 1
const DMI::TypeId TpMeqWMean(-1504);              // from /home/mevius/LOFAR/Timba/MeqNodes/src/WMean.h:30
const int TpMeqWMean_int = -1504;
namespace Meq { class WMean; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::WMean> : public TypeTraits<Meq::WMean>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqWMean_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::WMean & ContainerReturnType;
                typedef const Meq::WMean & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqWSRTCos3Beam
#define _defined_id_TpMeqWSRTCos3Beam 1
const DMI::TypeId TpMeqWSRTCos3Beam(-1750);       // from /home/oms/Timba/MeqNodes/src/WSRTCos3Beam.h:32
const int TpMeqWSRTCos3Beam_int = -1750;
namespace Meq { class WSRTCos3Beam; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::WSRTCos3Beam> : public TypeTraits<Meq::WSRTCos3Beam>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqWSRTCos3Beam_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::WSRTCos3Beam & ContainerReturnType;
                typedef const Meq::WSRTCos3Beam & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqWSum
#define _defined_id_TpMeqWSum 1
const DMI::TypeId TpMeqWSum(-1502);               // from /home/mevius/LOFAR/Timba/MeqNodes/src/WSum.h:30
const int TpMeqWSum_int = -1502;
namespace Meq { class WSum; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::WSum> : public TypeTraits<Meq::WSum>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqWSum_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::WSum & ContainerReturnType;
                typedef const Meq::WSum & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpMeqZeroFlagger
#define _defined_id_TpMeqZeroFlagger 1
const DMI::TypeId TpMeqZeroFlagger(-1434);        // from /home/oms/LOFAR/Timba/MeqNodes/src/ZeroFlagger.h:32
const int TpMeqZeroFlagger_int = -1434;
namespace Meq { class ZeroFlagger; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<Meq::ZeroFlagger> : public TypeTraits<Meq::ZeroFlagger>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpMeqZeroFlagger_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const Meq::ZeroFlagger & ContainerReturnType;
                typedef const Meq::ZeroFlagger & ContainerParamType;
              };
            };
#endif


#endif
