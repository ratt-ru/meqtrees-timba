    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../DMI/aid/build_aid_maps.pl
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
    
#include "Domain.h"
BlockableObject * __construct_MeqDomain (int n) { return n>0 ? new Meq::Domain [n] : new Meq::Domain; }
#include "Cells.h"
BlockableObject * __construct_MeqCells (int n) { return n>0 ? new Meq::Cells [n] : new Meq::Cells; }
#include "Request.h"
BlockableObject * __construct_MeqRequest (int n) { return n>0 ? new Meq::Request [n] : new Meq::Request; }
#include "VellSet.h"
BlockableObject * __construct_MeqVellSet (int n) { return n>0 ? new Meq::VellSet [n] : new Meq::VellSet; }
#include "Result.h"
BlockableObject * __construct_MeqResult (int n) { return n>0 ? new Meq::Result [n] : new Meq::Result; }
#include "Node.h"
BlockableObject * __construct_MeqNode (int n) { return n>0 ? new Meq::Node [n] : new Meq::Node; }
#include "Function.h"
BlockableObject * __construct_MeqFunction (int n) { return n>0 ? new Meq::Function [n] : new Meq::Function; }
#include "Polc.h"
BlockableObject * __construct_MeqPolc (int n) { return n>0 ? new Meq::Polc [n] : new Meq::Polc; }
  
    int aidRegistry_Meq ()
    {
      static int res = 

        AtomicID::registerId(-1233,"node")+
        AtomicID::registerId(-1248,"class")+
        AtomicID::registerId(-1188,"name")+
        AtomicID::registerId(-1060,"state")+
        AtomicID::registerId(-1226,"child")+
        AtomicID::registerId(-1220,"children")+
        AtomicID::registerId(-1210,"request")+
        AtomicID::registerId(-1228,"result")+
        AtomicID::registerId(-1368,"vellset")+
        AtomicID::registerId(-1250,"rider")+
        AtomicID::registerId(-1277,"command")+
        AtomicID::registerId(-1087,"id")+
        AtomicID::registerId(-1122,"group")+
        AtomicID::registerId(-1064,"add")+
        AtomicID::registerId(-1265,"update")+
        AtomicID::registerId(-1256,"value")+
        AtomicID::registerId(-1413,"values")+
        AtomicID::registerId(-1414,"solve")+
        AtomicID::registerId(-1339,"solver")+
        AtomicID::registerId(-1444,"dependency")+
        AtomicID::registerId(-1179,"resolution")+
        AtomicID::registerId(-1445,"depend")+
        AtomicID::registerId(-1287,"mask")+
        AtomicID::registerId(-1446,"resample")+
        AtomicID::registerId(-1160,"integrated")+
        AtomicID::registerId(-1247,"cells")+
        AtomicID::registerId(-1213,"domain")+
        AtomicID::registerId(-1128,"freq")+
        AtomicID::registerId(-1152,"time")+
        AtomicID::registerId(-1211,"calc")+
        AtomicID::registerId(-1230,"deriv")+
        AtomicID::registerId(-1370,"vells")+
        AtomicID::registerId(-1371,"vellsets")+
        AtomicID::registerId(-1298,"flags")+
        AtomicID::registerId(-1423,"weights")+
        AtomicID::registerId(-1285,"shape")+
        AtomicID::registerId(-1417,"grid")+
        AtomicID::registerId(-1418,"cell")+
        AtomicID::registerId(-1292,"size")+
        AtomicID::registerId(-1419,"segments")+
        AtomicID::registerId(-1105,"start")+
        AtomicID::registerId(-1283,"end")+
        AtomicID::registerId(-1363,"steps")+
        AtomicID::registerId(-1504,"axis")+
        AtomicID::registerId(-1415,"axes")+
        AtomicID::registerId(-1190,"offset")+
        AtomicID::registerId(-1324,"nodeindex")+
        AtomicID::registerId(-1361,"table")+
        AtomicID::registerId(-1231,"default")+
        AtomicID::registerId(-1051,"index")+
        AtomicID::registerId(-1177,"num")+
        AtomicID::registerId(-1375,"cache")+
        AtomicID::registerId(-1164,"code")+
        AtomicID::registerId(-1234,"parm")+
        AtomicID::registerId(-1254,"spid")+
        AtomicID::registerId(-1408,"coeff")+
        AtomicID::registerId(-1229,"perturbed")+
        AtomicID::registerId(-1218,"perturbations")+
        AtomicID::registerId(-1396,"names")+
        AtomicID::registerId(-1394,"pert")+
        AtomicID::registerId(-1393,"relative")+
        AtomicID::registerId(-1245,"results")+
        AtomicID::registerId(-1036,"fail")+
        AtomicID::registerId(-1132,"origin")+
        AtomicID::registerId(-1359,"line")+
        AtomicID::registerId(-1045,"message")+
        AtomicID::registerId(-1364,"contagious")+
        AtomicID::registerId(-1395,"normalized")+
        AtomicID::registerId(-1366,"solvable")+
        AtomicID::registerId(-1373,"config")+
        AtomicID::registerId(-1374,"groups")+
        AtomicID::registerId(-1381,"all")+
        AtomicID::registerId(-1382,"by")+
        AtomicID::registerId(-1046,"list")+
        AtomicID::registerId(-1412,"polc")+
        AtomicID::registerId(-1383,"polcs")+
        AtomicID::registerId(-1405,"scale")+
        AtomicID::registerId(-1422,"matrix")+
        AtomicID::registerId(-1411,"dbid")+
        AtomicID::registerId(-1409,"grow")+
        AtomicID::registerId(-1410,"inf")+
        AtomicID::registerId(-1189,"weight")+
        AtomicID::registerId(-1385,"epsilon")+
        AtomicID::registerId(-1384,"usesvd")+
        AtomicID::registerId(-1316,"set")+
        AtomicID::registerId(-1273,"auto")+
        AtomicID::registerId(-1391,"save")+
        AtomicID::registerId(-1389,"clear")+
        AtomicID::registerId(-1110,"invert")+
        AtomicID::registerId(-1404,"metrics")+
        AtomicID::registerId(-1402,"rank")+
        AtomicID::registerId(-1403,"fit")+
        AtomicID::registerId(-1397,"errors")+
        AtomicID::registerId(-1401,"covar")+
        AtomicID::registerId(-1135,"flag")+
        AtomicID::registerId(-1428,"bit")+
        AtomicID::registerId(-1400,"mu")+
        AtomicID::registerId(-1399,"stddev")+
        AtomicID::registerId(-1398,"chi")+
        AtomicID::registerId(-1421,"iter")+
        AtomicID::registerId(-1484,"last")+
        AtomicID::registerId(-1018,"l")+
        AtomicID::registerId(-1019,"m")+
        AtomicID::registerId(-1020,"n")+
        AtomicID::registerId(-1030,"x")+
        AtomicID::registerId(-1031,"y")+
        AtomicID::registerId(-1032,"z")+
        AtomicID::registerId(-1502,"lag")+
        AtomicID::registerId(-1235,"meqdomain")+
        TypeInfoReg::addToRegistry(-1235,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1235,__construct_MeqDomain)+
        AtomicID::registerId(-1416,"ndim")+
        AtomicID::registerId(-1415,"axes")+
        AtomicID::registerId(-1237,"meqcells")+
        TypeInfoReg::addToRegistry(-1237,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1237,__construct_MeqCells)+
        AtomicID::registerId(-1222,"meqrequest")+
        TypeInfoReg::addToRegistry(-1222,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1222,__construct_MeqRequest)+
        AtomicID::registerId(-1369,"meqvellset")+
        TypeInfoReg::addToRegistry(-1369,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1369,__construct_MeqVellSet)+
        AtomicID::registerId(-1246,"meqresult")+
        TypeInfoReg::addToRegistry(-1246,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1246,__construct_MeqResult)+
        AtomicID::registerId(-1242,"meqnode")+
        TypeInfoReg::addToRegistry(-1242,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1242,__construct_MeqNode)+
        AtomicID::registerId(-1451,"known")+
        AtomicID::registerId(-1453,"active")+
        AtomicID::registerId(-1458,"gen")+
        AtomicID::registerId(-1456,"dep")+
        AtomicID::registerId(-1457,"deps")+
        AtomicID::registerId(-1455,"symdep")+
        AtomicID::registerId(-1450,"symdeps")+
        AtomicID::registerId(-1454,"masks")+
        AtomicID::registerId(-1452,"dataset")+
        AtomicID::registerId(-1331,"resolve")+
        AtomicID::registerId(-1480,"parent")+
        AtomicID::registerId(-1091,"init")+
        AtomicID::registerId(-1460,"link")+
        AtomicID::registerId(-1461,"or")+
        AtomicID::registerId(-1332,"create")+
        AtomicID::registerId(-1131,"control")+
        AtomicID::registerId(-1216,"meqfunction")+
        TypeInfoReg::addToRegistry(-1216,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1216,__construct_MeqFunction)+
        AtomicID::registerId(-1407,"meqpolc")+
        TypeInfoReg::addToRegistry(-1407,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1407,__construct_MeqPolc)+
        AtomicID::registerId(-1335,"delete")+
    0;
    return res;
  }
  
  int __dum_call_registries_for_Meq = aidRegistry_Meq();

