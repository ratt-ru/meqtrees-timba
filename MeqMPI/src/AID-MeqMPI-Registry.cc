    // This file is generated automatically -- do not edit
    // Regenerate using "make aids"
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
#include "MPIProxy.h"
DMI::BObj * __construct_MeqMPIProxy (int n) { return n>0 ? new Meq::MPIProxy [n] : new Meq::MPIProxy; }
    using namespace DMI;
  
    int aidRegistry_MeqMPI ()
    {
      static int res = 

        AtomicID::registerId(-1073,"Remote")+
        AtomicID::registerId(-1738,"Proc")+
        AtomicID::registerId(-1103,"Data")+
        AtomicID::registerId(-1085,"Type")+
        AtomicID::registerId(-1056,"Error")+
        AtomicID::registerId(-1739,"MeqMPIProxy")+
        TypeInfoReg::addToRegistry(-1739,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1739,__construct_MeqMPIProxy)+
        AtomicID::registerId(-1204,"Command")+
        AtomicID::registerId(-1483,"Args")+
        AtomicID::registerId(-1226,"Request")+
        AtomicID::registerId(-1208,"Id")+
        AtomicID::registerId(-1573,"Verbose")+
    0;
    return res;
  }
  
  int __dum_call_registries_for_MeqMPI = aidRegistry_MeqMPI();

