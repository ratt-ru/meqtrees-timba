      #ifndef TID_DMI_h
      #define TID_DMI_h 1
      
      // This file is generated automatically -- do not edit
      // Generated by /home/oms/LOFAR/autoconf_share/../TIMBA/DMI/aid/build_aid_maps.pl
      #include <DMI/TypeId.h>

      // should be called somewhere in order to link in the registry
      int aidRegistry_DMI ();

#ifndef _defined_id_TpDMIAtomicID
#define _defined_id_TpDMIAtomicID 1
const DMI::TypeId TpDMIAtomicID(-1004);           // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:129
const int TpDMIAtomicID_int = -1004;
namespace DMI { class AtomicID; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::AtomicID> : public TypeTraits<DMI::AtomicID>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMIAtomicID_int };
                enum { TypeCategory = TypeCategories::BINARY };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::AtomicID & ContainerReturnType;
                typedef const DMI::AtomicID & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpDMIHIID
#define _defined_id_TpDMIHIID 1
const DMI::TypeId TpDMIHIID(-1005);               // from /home/oms/LOFAR/TIMBA/DMI/src/HIID.h:32
const int TpDMIHIID_int = -1005;
namespace DMI { class HIID; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::HIID> : public TypeTraits<DMI::HIID>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMIHIID_int };
                enum { TypeCategory = TypeCategories::SPECIAL };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::HIID & ContainerReturnType;
                typedef const DMI::HIID & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpDMIList
#define _defined_id_TpDMIList 1
const DMI::TypeId TpDMIList(-1002);               // from /home/oms/LOFAR/TIMBA/DMI/src/List.h:30
const int TpDMIList_int = -1002;
namespace DMI { class List; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::List> : public TypeTraits<DMI::List>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMIList_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::List & ContainerReturnType;
                typedef const DMI::List & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpDMINumArray
#define _defined_id_TpDMINumArray 1
const DMI::TypeId TpDMINumArray(-1003);           // from /home/oms/LOFAR/TIMBA/DMI/src/NumArray.h:176
const int TpDMINumArray_int = -1003;
namespace DMI { class NumArray; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::NumArray> : public TypeTraits<DMI::NumArray>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMINumArray_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::NumArray & ContainerReturnType;
                typedef const DMI::NumArray & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpDMIObjRef
#define _defined_id_TpDMIObjRef 1
const DMI::TypeId TpDMIObjRef(-1031);             // from /home/oms/LOFAR/TIMBA/DMI/src/BObj.h:32
const int TpDMIObjRef_int = -1031;
#endif
#ifndef _defined_id_TpDMIRecord
#define _defined_id_TpDMIRecord 1
const DMI::TypeId TpDMIRecord(-1018);             // from /home/oms/LOFAR/TIMBA/DMI/src/Record.h:30
const int TpDMIRecord_int = -1018;
namespace DMI { class Record; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::Record> : public TypeTraits<DMI::Record>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMIRecord_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::Record & ContainerReturnType;
                typedef const DMI::Record & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpDMITimestamp
#define _defined_id_TpDMITimestamp 1
const DMI::TypeId TpDMITimestamp(-1001);          // from /home/oms/LOFAR/TIMBA/DMI/src/Timestamp.h:7
const int TpDMITimestamp_int = -1001;
namespace DMI { class Timestamp; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::Timestamp> : public TypeTraits<DMI::Timestamp>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMITimestamp_int };
                enum { TypeCategory = TypeCategories::BINARY };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::Timestamp & ContainerReturnType;
                typedef const DMI::Timestamp & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_TpDMIVec
#define _defined_id_TpDMIVec 1
const DMI::TypeId TpDMIVec(-1006);                // from /home/oms/LOFAR/TIMBA/DMI/src/Vec.h:28
const int TpDMIVec_int = -1006;
namespace DMI { class Vec; };
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<DMI::Vec> : public TypeTraits<DMI::Vec>
              {
                public:
                enum { isContainable = true };
                enum { typeId = TpDMIVec_int };
                enum { TypeCategory = TypeCategories::DYNAMIC };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const DMI::Vec & ContainerReturnType;
                typedef const DMI::Vec & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpbool
#define _defined_id_Tpbool 1
const DMI::TypeId Tpbool(-32);                    // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:104
const int Tpbool_int = -32;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<bool> : public TypeTraits<bool>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpbool_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef bool ContainerReturnType;
                typedef bool ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpchar
#define _defined_id_Tpchar 1
const DMI::TypeId Tpchar(-33);                    // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:105
const int Tpchar_int = -33;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<char> : public TypeTraits<char>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpchar_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef char ContainerReturnType;
                typedef char ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpdcomplex
#define _defined_id_Tpdcomplex 1
const DMI::TypeId Tpdcomplex(-47);                // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:108
const int Tpdcomplex_int = -47;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<dcomplex> : public TypeTraits<dcomplex>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpdcomplex_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef dcomplex ContainerReturnType;
                typedef dcomplex ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpdouble
#define _defined_id_Tpdouble 1
const DMI::TypeId Tpdouble(-44);                  // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:107
const int Tpdouble_int = -44;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<double> : public TypeTraits<double>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpdouble_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef double ContainerReturnType;
                typedef double ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpfcomplex
#define _defined_id_Tpfcomplex 1
const DMI::TypeId Tpfcomplex(-46);                // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:108
const int Tpfcomplex_int = -46;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<fcomplex> : public TypeTraits<fcomplex>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpfcomplex_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef fcomplex ContainerReturnType;
                typedef fcomplex ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpfloat
#define _defined_id_Tpfloat 1
const DMI::TypeId Tpfloat(-43);                   // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:107
const int Tpfloat_int = -43;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<float> : public TypeTraits<float>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpfloat_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef float ContainerReturnType;
                typedef float ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpint
#define _defined_id_Tpint 1
const DMI::TypeId Tpint(-37);                     // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:105
const int Tpint_int = -37;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<int> : public TypeTraits<int>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpint_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef int ContainerReturnType;
                typedef int ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpldouble
#define _defined_id_Tpldouble 1
const DMI::TypeId Tpldouble(-45);                 // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:107
const int Tpldouble_int = -45;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<ldouble> : public TypeTraits<ldouble>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpldouble_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef ldouble ContainerReturnType;
                typedef ldouble ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tplong
#define _defined_id_Tplong 1
const DMI::TypeId Tplong(-39);                    // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:106
const int Tplong_int = -39;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<long> : public TypeTraits<long>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tplong_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef long ContainerReturnType;
                typedef long ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tplonglong
#define _defined_id_Tplonglong 1
const DMI::TypeId Tplonglong(-41);                // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:106
const int Tplonglong_int = -41;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<longlong> : public TypeTraits<longlong>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tplonglong_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef longlong ContainerReturnType;
                typedef longlong ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpshort
#define _defined_id_Tpshort 1
const DMI::TypeId Tpshort(-35);                   // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:105
const int Tpshort_int = -35;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<short> : public TypeTraits<short>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpshort_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef short ContainerReturnType;
                typedef short ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpstring
#define _defined_id_Tpstring 1
const DMI::TypeId Tpstring(-48);                  // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:109
const int Tpstring_int = -48;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<string> : public TypeTraits<string>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpstring_int };
                enum { TypeCategory = TypeCategories::SPECIAL };
                enum { ParamByRef = true, ReturnByRef = true };
                typedef const string & ContainerReturnType;
                typedef const string & ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpuchar
#define _defined_id_Tpuchar 1
const DMI::TypeId Tpuchar(-34);                   // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:105
const int Tpuchar_int = -34;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<uchar> : public TypeTraits<uchar>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpuchar_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef uchar ContainerReturnType;
                typedef uchar ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpuint
#define _defined_id_Tpuint 1
const DMI::TypeId Tpuint(-38);                    // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:105
const int Tpuint_int = -38;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<uint> : public TypeTraits<uint>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpuint_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef uint ContainerReturnType;
                typedef uint ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpulong
#define _defined_id_Tpulong 1
const DMI::TypeId Tpulong(-40);                   // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:106
const int Tpulong_int = -40;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<ulong> : public TypeTraits<ulong>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpulong_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef ulong ContainerReturnType;
                typedef ulong ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpulonglong
#define _defined_id_Tpulonglong 1
const DMI::TypeId Tpulonglong(-42);               // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:106
const int Tpulonglong_int = -42;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<ulonglong> : public TypeTraits<ulonglong>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpulonglong_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef ulonglong ContainerReturnType;
                typedef ulonglong ContainerParamType;
              };
            };
#endif
#ifndef _defined_id_Tpushort
#define _defined_id_Tpushort 1
const DMI::TypeId Tpushort(-36);                  // from /home/oms/LOFAR/TIMBA/DMI/src/TypeId.h:105
const int Tpushort_int = -36;
            namespace DMI {
              template<>
              class DMIBaseTypeTraits<ushort> : public TypeTraits<ushort>
              {
                public:
                enum { isContainable = true };
                enum { typeId = Tpushort_int };
                enum { TypeCategory = TypeCategories::NUMERIC };
                enum { ParamByRef = false, ReturnByRef = false };
                typedef ushort ContainerReturnType;
                typedef ushort ContainerParamType;
              };
            };
#endif


#endif
