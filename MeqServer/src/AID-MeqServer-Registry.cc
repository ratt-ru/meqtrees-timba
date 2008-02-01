    // This file is generated automatically -- do not edit
    // Regenerate using "make aids"
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
#include "VisDataMux.h"
DMI::BObj * __construct_MeqVisDataMux (int n) { return n>0 ? new Meq::VisDataMux [n] : new Meq::VisDataMux; }
#include "Sink.h"
DMI::BObj * __construct_MeqSink (int n) { return n>0 ? new Meq::Sink [n] : new Meq::Sink; }
#include "Spigot.h"
DMI::BObj * __construct_MeqSpigot (int n) { return n>0 ? new Meq::Spigot [n] : new Meq::Spigot; }
#include "PyNode.h"
DMI::BObj * __construct_MeqPyNode (int n) { return n>0 ? new Meq::PyNode [n] : new Meq::PyNode; }
#include "PyTensorFuncNode.h"
DMI::BObj * __construct_MeqPyTensorFuncNode (int n) { return n>0 ? new Meq::PyTensorFuncNode [n] : new Meq::PyTensorFuncNode; }
    using namespace DMI;
  
    int aidRegistry_MeqServer ()
    {
      static int res = 

        AtomicID::registerId(-1544,"MeqClient")+
        AtomicID::registerId(-1288,"Node")+
        AtomicID::registerId(-1122,"Name")+
        AtomicID::registerId(-1338,"NodeIndex")+
        AtomicID::registerId(-1462,"MeqServer")+
        AtomicID::registerId(-1622,"Meq")+
        AtomicID::registerId(-1553,"CWD")+
        AtomicID::registerId(-1312,"Create")+
        AtomicID::registerId(-1336,"Delete")+
        AtomicID::registerId(-1467,"Get")+
        AtomicID::registerId(-1272,"Set")+
        AtomicID::registerId(-1072,"State")+
        AtomicID::registerId(-1226,"Request")+
        AtomicID::registerId(-1317,"Resolve")+
        AtomicID::registerId(-1314,"Child")+
        AtomicID::registerId(-1305,"Children")+
        AtomicID::registerId(-1040,"List")+
        AtomicID::registerId(-1563,"Batch")+
        AtomicID::registerId(-1203,"App")+
        AtomicID::registerId(-1204,"Command")+
        AtomicID::registerId(-1483,"Args")+
        AtomicID::registerId(-1242,"Result")+
        AtomicID::registerId(-1103,"Data")+
        AtomicID::registerId(-1484,"Processing")+
        AtomicID::registerId(-1056,"Error")+
        AtomicID::registerId(-1269,"Message")+
        AtomicID::registerId(-1120,"Code")+
        AtomicID::registerId(-1479,"Execute")+
        AtomicID::registerId(-1353,"Clear")+
        AtomicID::registerId(-1316,"Cache")+
        AtomicID::registerId(-1332,"Save")+
        AtomicID::registerId(-1463,"Load")+
        AtomicID::registerId(-1476,"Forest")+
        AtomicID::registerId(-1478,"Recursive")+
        AtomicID::registerId(-1201,"Header")+
        AtomicID::registerId(-1512,"Version")+
        AtomicID::registerId(-1060,"Publish")+
        AtomicID::registerId(-1330,"Results")+
        AtomicID::registerId(-1465,"Enable")+
        AtomicID::registerId(-1471,"Disable")+
        AtomicID::registerId(-1080,"Event")+
        AtomicID::registerId(-1208,"Id")+
        AtomicID::registerId(-1490,"Silent")+
        AtomicID::registerId(-1477,"Idle")+
        AtomicID::registerId(-1268,"Stream")+
        AtomicID::registerId(-1482,"Debug")+
        AtomicID::registerId(-1359,"Breakpoint")+
        AtomicID::registerId(-1315,"Single")+
        AtomicID::registerId(-1348,"Shot")+
        AtomicID::registerId(-1473,"Step")+
        AtomicID::registerId(-1474,"Continue")+
        AtomicID::registerId(-1475,"Until")+
        AtomicID::registerId(-1247,"Stop")+
        AtomicID::registerId(-1047,"Level")+
        AtomicID::registerId(-1209,"Status")+
        AtomicID::registerId(-1466,"Stack")+
        AtomicID::registerId(-1472,"Running")+
        AtomicID::registerId(-1510,"Changed")+
        AtomicID::registerId(-1286,"All")+
        AtomicID::registerId(-1511,"Disabled")+
        AtomicID::registerId(-1509,"Publishing")+
        AtomicID::registerId(-1113,"Python")+
        AtomicID::registerId(-1038,"Init")+
        AtomicID::registerId(-1564,"TDL")+
        AtomicID::registerId(-1565,"Script")+
        AtomicID::registerId(-1224,"File")+
        AtomicID::registerId(-1162,"Source")+
        AtomicID::registerId(-1597,"Serial")+
        AtomicID::registerId(-48,"String")+
        AtomicID::registerId(-1733,"Session")+
        AtomicID::registerId(-1623,"Executing")+
        AtomicID::registerId(-1651,"Exec")+
        AtomicID::registerId(-1645,"Constructing")+
        AtomicID::registerId(-1650,"Updating")+
        AtomicID::registerId(-1624,"Sync")+
        AtomicID::registerId(-1649,"Stopped")+
        AtomicID::registerId(-1585,"MeqVisDataMux")+
        TypeInfoReg::addToRegistry(-1585,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1585,__construct_MeqVisDataMux)+
        AtomicID::registerId(-1131,"Station")+
        AtomicID::registerId(-1061,"Index")+
        AtomicID::registerId(-1232,"Tile")+
        AtomicID::registerId(-1261,"Format")+
        AtomicID::registerId(-1106,"Start")+
        AtomicID::registerId(-1584,"Pre")+
        AtomicID::registerId(-1231,"Post")+
        AtomicID::registerId(-1625,"Chunks")+
        AtomicID::registerId(-1045,"Open")+
        AtomicID::registerId(-1252,"Closed")+
        AtomicID::registerId(-1635,"Current")+
        AtomicID::registerId(-1640,"Timeslots")+
        AtomicID::registerId(-1487,"VisHandlerNode")+
        AtomicID::registerId(-1163,"Num")+
        AtomicID::registerId(-1202,"Antenna")+
        AtomicID::registerId(-1036,"Input")+
        AtomicID::registerId(-1241,"Output")+
        AtomicID::registerId(-1489,"Col")+
        AtomicID::registerId(-1188,"Corr")+
        AtomicID::registerId(-1480,"Next")+
        AtomicID::registerId(-1488,"Read")+
        AtomicID::registerId(-1134,"Flag")+
        AtomicID::registerId(-1253,"Flags")+
        AtomicID::registerId(-1263,"Mask")+
        AtomicID::registerId(-1153,"Row")+
        AtomicID::registerId(-1486,"Mandate")+
        AtomicID::registerId(-1464,"Regular")+
        AtomicID::registerId(-1302,"Grid")+
        AtomicID::registerId(-1123,"UVW")+
        AtomicID::registerId(-1166,"Group")+
        AtomicID::registerId(-1470,"Sink")+
        AtomicID::registerId(-1481,"MeqSink")+
        TypeInfoReg::addToRegistry(-1481,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1481,__construct_MeqSink)+
        AtomicID::registerId(-1485,"Spigot")+
        AtomicID::registerId(-1469,"Queue")+
        AtomicID::registerId(-1468,"MeqSpigot")+
        TypeInfoReg::addToRegistry(-1468,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1468,__construct_MeqSpigot)+
        AtomicID::registerId(-1705,"MeqPyNode")+
        TypeInfoReg::addToRegistry(-1705,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1705,__construct_MeqPyNode)+
        AtomicID::registerId(-1371,"Class")+
        AtomicID::registerId(-1706,"Module")+
        AtomicID::registerId(-1721,"MeqPyTensorFuncNode")+
        TypeInfoReg::addToRegistry(-1721,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1721,__construct_MeqPyTensorFuncNode)+
    0;
    return res;
  }
  
  int __dum_call_registries_for_MeqServer = aidRegistry_MeqServer();

