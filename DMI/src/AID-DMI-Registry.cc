    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../DMI/aid/build_aid_maps.pl
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
    
#include "DataArray.h"
BlockableObject * __construct_DataArray (int n) { return n>0 ? new DataArray [n] : new DataArray; }
#include "DataField.h"
BlockableObject * __construct_DataField (int n) { return n>0 ? new DataField [n] : new DataField; }
#include "DataRecord.h"
BlockableObject * __construct_DataRecord (int n) { return n>0 ? new DataRecord [n] : new DataRecord; }
#include "HIID.h"
        void * __new_HIID  (int n) 
        { return new HIID [n]; }  
        void __delete_HIID (void *ptr) 
        { delete [] static_cast<HIID*>(ptr); } 
        void __copy_HIID (void *to,const void *from) 
        { *static_cast<HIID*>(to) = *static_cast<const HIID*>(from); } 
        size_t __pack_HIID (const void *arr,int n,void * block,size_t &nleft ) 
        { return ArrayPacker<HIID>::pack(static_cast<const HIID*>(arr),n,block,nleft); } 
        void * __unpack_HIID (const void *block,size_t sz,int &n) 
        { return ArrayPacker<HIID>::allocate(block,sz,n); } 
        size_t __packsize_HIID (const void *arr,int n) 
        { return ArrayPacker<HIID>::packSize(static_cast<const HIID*>(arr),n); }
#include "Timestamp.h"
        void * __new_string  (int n) 
        { return new string [n]; }  
        void __delete_string (void *ptr) 
        { delete [] static_cast<string*>(ptr); } 
        void __copy_string (void *to,const void *from) 
        { *static_cast<string*>(to) = *static_cast<const string*>(from); } 
        size_t __pack_string (const void *arr,int n,void * block,size_t &nleft ) 
        { return ArrayPacker<string>::pack(static_cast<const string*>(arr),n,block,nleft); } 
        void * __unpack_string (const void *block,size_t sz,int &n) 
        { return ArrayPacker<string>::allocate(block,sz,n); } 
        size_t __packsize_string (const void *arr,int n) 
        { return ArrayPacker<string>::packSize(static_cast<const string*>(arr),n); }
#include "TypeId.h"
  
    int aidRegistry_DMI ()
    {
      static int res = 

        AtomicID::registerId(-1001,"A")+
        AtomicID::registerId(-1002,"B")+
        AtomicID::registerId(-1003,"C")+
        AtomicID::registerId(-1004,"D")+
        AtomicID::registerId(-1005,"E")+
        AtomicID::registerId(-1006,"F")+
        AtomicID::registerId(-1008,"G")+
        AtomicID::registerId(-1009,"H")+
        AtomicID::registerId(-1010,"I")+
        AtomicID::registerId(-1011,"J")+
        AtomicID::registerId(-1012,"K")+
        AtomicID::registerId(-1013,"L")+
        AtomicID::registerId(-1014,"M")+
        AtomicID::registerId(-1015,"N")+
        AtomicID::registerId(-1016,"O")+
        AtomicID::registerId(-1017,"P")+
        AtomicID::registerId(-1018,"Q")+
        AtomicID::registerId(-1019,"R")+
        AtomicID::registerId(-1020,"S")+
        AtomicID::registerId(-1021,"T")+
        AtomicID::registerId(-1023,"U")+
        AtomicID::registerId(-1024,"V")+
        AtomicID::registerId(-1026,"W")+
        AtomicID::registerId(-1027,"X")+
        AtomicID::registerId(-1028,"Y")+
        AtomicID::registerId(-1029,"Z")+
        AtomicID::registerId(-1030,"ObjRef")+
        TypeInfoReg::addToRegistry(-1030,TypeInfo(TypeInfo::OTHER,0))+
        AtomicID::registerId(-1022,"DataArray")+
        TypeInfoReg::addToRegistry(-1022,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1022,__construct_DataArray)+
        AtomicID::registerId(-1031,"DataField")+
        TypeInfoReg::addToRegistry(-1031,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1031,__construct_DataField)+
        AtomicID::registerId(-1033,"DataRecord")+
        TypeInfoReg::addToRegistry(-1033,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1033,__construct_DataRecord)+
        AtomicID::registerId(-1025,"HIID")+
        TypeInfoReg::addToRegistry(-1025,TypeInfo(TypeInfo::SPECIAL,sizeof(HIID),__new_HIID,__delete_HIID,__copy_HIID,
                __pack_HIID,__unpack_HIID,__packsize_HIID))+
        AtomicID::registerId(-1032,"Timestamp")+
        TypeInfoReg::addToRegistry(-1032,TypeInfo(TypeInfo::BINARY,sizeof(Timestamp)))+
        AtomicID::registerId(-32,"bool")+
        TypeInfoReg::addToRegistry(-32,TypeInfo(TypeInfo::NUMERIC,sizeof(bool)))+
        AtomicID::registerId(-33,"char")+
        TypeInfoReg::addToRegistry(-33,TypeInfo(TypeInfo::NUMERIC,sizeof(char)))+
        AtomicID::registerId(-34,"uchar")+
        TypeInfoReg::addToRegistry(-34,TypeInfo(TypeInfo::NUMERIC,sizeof(uchar)))+
        AtomicID::registerId(-35,"short")+
        TypeInfoReg::addToRegistry(-35,TypeInfo(TypeInfo::NUMERIC,sizeof(short)))+
        AtomicID::registerId(-36,"ushort")+
        TypeInfoReg::addToRegistry(-36,TypeInfo(TypeInfo::NUMERIC,sizeof(ushort)))+
        AtomicID::registerId(-37,"int")+
        TypeInfoReg::addToRegistry(-37,TypeInfo(TypeInfo::NUMERIC,sizeof(int)))+
        AtomicID::registerId(-38,"uint")+
        TypeInfoReg::addToRegistry(-38,TypeInfo(TypeInfo::NUMERIC,sizeof(uint)))+
        AtomicID::registerId(-39,"long")+
        TypeInfoReg::addToRegistry(-39,TypeInfo(TypeInfo::NUMERIC,sizeof(long)))+
        AtomicID::registerId(-40,"ulong")+
        TypeInfoReg::addToRegistry(-40,TypeInfo(TypeInfo::NUMERIC,sizeof(ulong)))+
        AtomicID::registerId(-41,"longlong")+
        TypeInfoReg::addToRegistry(-41,TypeInfo(TypeInfo::NUMERIC,sizeof(longlong)))+
        AtomicID::registerId(-42,"ulonglong")+
        TypeInfoReg::addToRegistry(-42,TypeInfo(TypeInfo::NUMERIC,sizeof(ulonglong)))+
        AtomicID::registerId(-43,"float")+
        TypeInfoReg::addToRegistry(-43,TypeInfo(TypeInfo::NUMERIC,sizeof(float)))+
        AtomicID::registerId(-44,"double")+
        TypeInfoReg::addToRegistry(-44,TypeInfo(TypeInfo::NUMERIC,sizeof(double)))+
        AtomicID::registerId(-45,"ldouble")+
        TypeInfoReg::addToRegistry(-45,TypeInfo(TypeInfo::NUMERIC,sizeof(ldouble)))+
        AtomicID::registerId(-46,"fcomplex")+
        TypeInfoReg::addToRegistry(-46,TypeInfo(TypeInfo::NUMERIC,sizeof(fcomplex)))+
        AtomicID::registerId(-47,"dcomplex")+
        TypeInfoReg::addToRegistry(-47,TypeInfo(TypeInfo::NUMERIC,sizeof(dcomplex)))+
        AtomicID::registerId(-48,"string")+
        TypeInfoReg::addToRegistry(-48,TypeInfo(TypeInfo::SPECIAL,sizeof(string),__new_string,__delete_string,__copy_string,
                __pack_string,__unpack_string,__packsize_string))+
        AtomicID::registerId(-1007,"AtomicID")+
        TypeInfoReg::addToRegistry(-1007,TypeInfo(TypeInfo::BINARY,sizeof(AtomicID)))+
    0;
    return res;
  }
  
  int __dum_call_registries_for_DMI = aidRegistry_DMI();

