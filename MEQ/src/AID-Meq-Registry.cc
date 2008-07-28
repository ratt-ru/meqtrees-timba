    // This file is generated automatically -- do not edit
    // Regenerate using "make aids"
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
#include "Domain.h"
DMI::BObj * __construct_MeqDomain (int n) { return n>0 ? new Meq::Domain [n] : new Meq::Domain; }
#include "Cells.h"
DMI::BObj * __construct_MeqCells (int n) { return n>0 ? new Meq::Cells [n] : new Meq::Cells; }
#include "Request.h"
DMI::BObj * __construct_MeqRequest (int n) { return n>0 ? new Meq::Request [n] : new Meq::Request; }
#include "Vells.h"
DMI::BObj * __construct_MeqVells (int n) { return n>0 ? new Meq::Vells [n] : new Meq::Vells; }
#include "VellSet.h"
DMI::BObj * __construct_MeqVellSet (int n) { return n>0 ? new Meq::VellSet [n] : new Meq::VellSet; }
#include "Result.h"
DMI::BObj * __construct_MeqResult (int n) { return n>0 ? new Meq::Result [n] : new Meq::Result; }
#include "Funklet.h"
DMI::BObj * __construct_MeqFunklet (int n) { return n>0 ? new Meq::Funklet [n] : new Meq::Funklet; }
#include "Polc.h"
DMI::BObj * __construct_MeqPolc (int n) { return n>0 ? new Meq::Polc [n] : new Meq::Polc; }
#include "ComposedPolc.h"
DMI::BObj * __construct_MeqComposedPolc (int n) { return n>0 ? new Meq::ComposedPolc [n] : new Meq::ComposedPolc; }
#include "PolcLog.h"
DMI::BObj * __construct_MeqPolcLog (int n) { return n>0 ? new Meq::PolcLog [n] : new Meq::PolcLog; }
#include "Node.h"
DMI::BObj * __construct_MeqNode (int n) { return n>0 ? new Meq::Node [n] : new Meq::Node; }
#include "Function.h"
DMI::BObj * __construct_MeqFunction (int n) { return n>0 ? new Meq::Function [n] : new Meq::Function; }
#include "Spline.h"
DMI::BObj * __construct_MeqSpline (int n) { return n>0 ? new Meq::Spline [n] : new Meq::Spline; }
    using namespace DMI;
  
    int aidRegistry_Meq ()
    {
      static int res = 

        AtomicID::registerId(-1288,"Node")+
        AtomicID::registerId(-1371,"Class")+
        AtomicID::registerId(-1122,"Name")+
        AtomicID::registerId(-1072,"State")+
        AtomicID::registerId(-1314,"Child")+
        AtomicID::registerId(-1305,"Children")+
        AtomicID::registerId(-1226,"Request")+
        AtomicID::registerId(-1242,"Result")+
        AtomicID::registerId(-1365,"VellSet")+
        AtomicID::registerId(-1331,"Rider")+
        AtomicID::registerId(-1204,"Command")+
        AtomicID::registerId(-1208,"Id")+
        AtomicID::registerId(-1166,"Group")+
        AtomicID::registerId(-1088,"Add")+
        AtomicID::registerId(-1229,"Update")+
        AtomicID::registerId(-1233,"Value")+
        AtomicID::registerId(-1296,"Values")+
        AtomicID::registerId(-1374,"Solve")+
        AtomicID::registerId(-1373,"Solver")+
        AtomicID::registerId(-1300,"Dependency")+
        AtomicID::registerId(-1191,"Resolution")+
        AtomicID::registerId(-1364,"Depend")+
        AtomicID::registerId(-1263,"Mask")+
        AtomicID::registerId(-1319,"Resample")+
        AtomicID::registerId(-1181,"Integrated")+
        AtomicID::registerId(-1513,"Dims")+
        AtomicID::registerId(-1291,"Cells")+
        AtomicID::registerId(-1256,"Domain")+
        AtomicID::registerId(-1177,"Freq")+
        AtomicID::registerId(-1126,"Time")+
        AtomicID::registerId(-1290,"Calc")+
        AtomicID::registerId(-1324,"Deriv")+
        AtomicID::registerId(-1352,"Vells")+
        AtomicID::registerId(-1280,"VellSets")+
        AtomicID::registerId(-1253,"Flags")+
        AtomicID::registerId(-1285,"Weights")+
        AtomicID::registerId(-1278,"Shape")+
        AtomicID::registerId(-1302,"Grid")+
        AtomicID::registerId(-1301,"Cell")+
        AtomicID::registerId(-1255,"Size")+
        AtomicID::registerId(-1287,"Segments")+
        AtomicID::registerId(-1106,"Start")+
        AtomicID::registerId(-1276,"End")+
        AtomicID::registerId(-1284,"Steps")+
        AtomicID::registerId(-1318,"Axis")+
        AtomicID::registerId(-1346,"Axes")+
        AtomicID::registerId(-1195,"Offset")+
        AtomicID::registerId(-1338,"NodeIndex")+
        AtomicID::registerId(-1354,"Table")+
        AtomicID::registerId(-1221,"Default")+
        AtomicID::registerId(-1061,"Index")+
        AtomicID::registerId(-1163,"Num")+
        AtomicID::registerId(-1316,"Cache")+
        AtomicID::registerId(-1120,"Code")+
        AtomicID::registerId(-1306,"Funklet")+
        AtomicID::registerId(-1313,"Funklets")+
        AtomicID::registerId(-1578,"Function")+
        AtomicID::registerId(-1379,"Parm")+
        AtomicID::registerId(-1340,"Spid")+
        AtomicID::registerId(-1356,"Coeff")+
        AtomicID::registerId(-1372,"Perturbed")+
        AtomicID::registerId(-1367,"Perturbations")+
        AtomicID::registerId(-1328,"Names")+
        AtomicID::registerId(-1325,"Pert")+
        AtomicID::registerId(-1333,"Relative")+
        AtomicID::registerId(-1330,"Results")+
        AtomicID::registerId(-1248,"Fail")+
        AtomicID::registerId(-1185,"Origin")+
        AtomicID::registerId(-1358,"Line")+
        AtomicID::registerId(-1269,"Message")+
        AtomicID::registerId(-1366,"Contagious")+
        AtomicID::registerId(-1334,"Normalized")+
        AtomicID::registerId(-1292,"Solvable")+
        AtomicID::registerId(-1329,"Config")+
        AtomicID::registerId(-1369,"Groups")+
        AtomicID::registerId(-1286,"All")+
        AtomicID::registerId(-1297,"By")+
        AtomicID::registerId(-1040,"List")+
        AtomicID::registerId(-1298,"Polc")+
        AtomicID::registerId(-1308,"Polcs")+
        AtomicID::registerId(-1323,"Scale")+
        AtomicID::registerId(-1345,"Matrix")+
        AtomicID::registerId(-1343,"DbId")+
        AtomicID::registerId(-1355,"Grow")+
        AtomicID::registerId(-1282,"Inf")+
        AtomicID::registerId(-1137,"Weight")+
        AtomicID::registerId(-1377,"Epsilon")+
        AtomicID::registerId(-1335,"UseSVD")+
        AtomicID::registerId(-1272,"Set")+
        AtomicID::registerId(-1213,"Auto")+
        AtomicID::registerId(-1332,"Save")+
        AtomicID::registerId(-1353,"Clear")+
        AtomicID::registerId(-1102,"Invert")+
        AtomicID::registerId(-1587,"Use")+
        AtomicID::registerId(-1586,"Previous")+
        AtomicID::registerId(-1652,"Reset")+
        AtomicID::registerId(-1363,"Metrics")+
        AtomicID::registerId(-1304,"Rank")+
        AtomicID::registerId(-1281,"Fit")+
        AtomicID::registerId(-1310,"Errors")+
        AtomicID::registerId(-1299,"CoVar")+
        AtomicID::registerId(-1134,"Flag")+
        AtomicID::registerId(-1293,"Bit")+
        AtomicID::registerId(-1362,"Mu")+
        AtomicID::registerId(-1350,"StdDev")+
        AtomicID::registerId(-1289,"Chi")+
        AtomicID::registerId(-1370,"Iter")+
        AtomicID::registerId(-1342,"Last")+
        AtomicID::registerId(-1337,"Override")+
        AtomicID::registerId(-1529,"Policy")+
        AtomicID::registerId(-1556,"Discover")+
        AtomicID::registerId(-1555,"Spids")+
        AtomicID::registerId(-1216,"Map")+
        AtomicID::registerId(-1557,"Eval")+
        AtomicID::registerId(-1215,"Mode")+
        AtomicID::registerId(-1661,"Incr")+
        AtomicID::registerId(-1266,"Iteration")+
        AtomicID::registerId(-1525,"Solution")+
        AtomicID::registerId(-1376,"Dataset")+
        AtomicID::registerId(-1480,"Next")+
        AtomicID::registerId(-1558,"Service")+
        AtomicID::registerId(-1559,"Sequence")+
        AtomicID::registerId(-1703,"Spline")+
        AtomicID::registerId(-1232,"Tile")+
        AtomicID::registerId(-1561,"Tiled")+
        AtomicID::registerId(-1262,"Tiles")+
        AtomicID::registerId(-1562,"Tiling")+
        AtomicID::registerId(-1560,"Sizes")+
        AtomicID::registerId(-1670,"Constrain")+
        AtomicID::registerId(-1498,"Force")+
        AtomicID::registerId(-1671,"Positive")+
        AtomicID::registerId(-1672,"Negative")+
        AtomicID::registerId(-1674,"Cyclic")+
        AtomicID::registerId(-1675,"Min")+
        AtomicID::registerId(-1070,"Max")+
        AtomicID::registerId(-1697,"Lib")+
        AtomicID::registerId(-1032,"L")+
        AtomicID::registerId(-1030,"M")+
        AtomicID::registerId(-1028,"N")+
        AtomicID::registerId(-1024,"X")+
        AtomicID::registerId(-1005,"Y")+
        AtomicID::registerId(-1021,"Z")+
        AtomicID::registerId(-1006,"U")+
        AtomicID::registerId(-1014,"V")+
        AtomicID::registerId(-1022,"W")+
        AtomicID::registerId(-1435,"RA")+
        AtomicID::registerId(-1446,"Dec")+
        AtomicID::registerId(-1303,"Lag")+
        AtomicID::registerId(-1294,"MeqDomain")+
        TypeInfoReg::addToRegistry(-1294,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1294,__construct_MeqDomain)+
        AtomicID::registerId(-1309,"ndim")+
        AtomicID::registerId(-1346,"axes")+
        AtomicID::registerId(-1339,"MeqCells")+
        TypeInfoReg::addToRegistry(-1339,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1339,__construct_MeqCells)+
        AtomicID::registerId(-1357,"MeqRequest")+
        TypeInfoReg::addToRegistry(-1357,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1357,__construct_MeqRequest)+
        AtomicID::registerId(-1279,"Reexecute")+
        AtomicID::registerId(-1619,"st")+
        AtomicID::registerId(-1620,"ev")+
        AtomicID::registerId(-1617,"e0")+
        AtomicID::registerId(-1618,"e1")+
        AtomicID::registerId(-1615,"e2")+
        AtomicID::registerId(-1616,"ds")+
        AtomicID::registerId(-1614,"pu")+
        AtomicID::registerId(-1341,"MeqVells")+
        TypeInfoReg::addToRegistry(-1341,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1341,__construct_MeqVells)+
        AtomicID::registerId(-1307,"MeqVellSet")+
        TypeInfoReg::addToRegistry(-1307,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1307,__construct_MeqVellSet)+
        AtomicID::registerId(-1360,"MeqResult")+
        TypeInfoReg::addToRegistry(-1360,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1360,__construct_MeqResult)+
        AtomicID::registerId(-1321,"MeqFunklet")+
        TypeInfoReg::addToRegistry(-1321,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1321,__construct_MeqFunklet)+
        AtomicID::registerId(-1361,"MeqPolc")+
        TypeInfoReg::addToRegistry(-1361,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1361,__construct_MeqPolc)+
        AtomicID::registerId(-1582,"MeqComposedPolc")+
        TypeInfoReg::addToRegistry(-1582,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1582,__construct_MeqComposedPolc)+
        AtomicID::registerId(-1549,"MeqPolcLog")+
        TypeInfoReg::addToRegistry(-1549,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1549,__construct_MeqPolcLog)+
        AtomicID::registerId(-1378,"MeqNode")+
        TypeInfoReg::addToRegistry(-1378,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1378,__construct_MeqNode)+
        AtomicID::registerId(-1347,"Known")+
        AtomicID::registerId(-1349,"Active")+
        AtomicID::registerId(-1351,"Gen")+
        AtomicID::registerId(-1326,"Dep")+
        AtomicID::registerId(-1327,"Deps")+
        AtomicID::registerId(-1311,"Symdep")+
        AtomicID::registerId(-1322,"Symdeps")+
        AtomicID::registerId(-1344,"Masks")+
        AtomicID::registerId(-1741,"Depth")+
        AtomicID::registerId(-1635,"Current")+
        AtomicID::registerId(-1317,"Resolve")+
        AtomicID::registerId(-1295,"Parent")+
        AtomicID::registerId(-1038,"Init")+
        AtomicID::registerId(-1375,"Link")+
        AtomicID::registerId(-1368,"Or")+
        AtomicID::registerId(-1312,"Create")+
        AtomicID::registerId(-1142,"Control")+
        AtomicID::registerId(-1209,"Status")+
        AtomicID::registerId(-1320,"New")+
        AtomicID::registerId(-1359,"Breakpoint")+
        AtomicID::registerId(-1315,"Single")+
        AtomicID::registerId(-1348,"Shot")+
        AtomicID::registerId(-1473,"Step")+
        AtomicID::registerId(-1531,"Stats")+
        AtomicID::registerId(-1532,"Requests")+
        AtomicID::registerId(-1530,"Parents")+
        AtomicID::registerId(-1581,"Description")+
        AtomicID::registerId(-1536,"Profiling")+
        AtomicID::registerId(-1139,"Total")+
        AtomicID::registerId(-1467,"Get")+
        AtomicID::registerId(-1533,"Ticks")+
        AtomicID::registerId(-1534,"Per")+
        AtomicID::registerId(-1535,"Second")+
        AtomicID::registerId(-1539,"CPU")+
        AtomicID::registerId(-1538,"MHz")+
        AtomicID::registerId(-1602,"Poll")+
        AtomicID::registerId(-1603,"Polling")+
        AtomicID::registerId(-1601,"Order")+
        AtomicID::registerId(-1604,"MT")+
        AtomicID::registerId(-1606,"Propagate")+
        AtomicID::registerId(-1605,"Fails")+
        AtomicID::registerId(-1056,"Error")+
        AtomicID::registerId(-1103,"Data")+
        AtomicID::registerId(-1659,"Indices")+
        AtomicID::registerId(-1658,"Is")+
        AtomicID::registerId(-1660,"Internal")+
        AtomicID::registerId(-1509,"Publishing")+
        AtomicID::registerId(-1047,"Level")+
        AtomicID::registerId(-1478,"Recursive")+
        AtomicID::registerId(-1724,"Log")+
        AtomicID::registerId(-1657,"Missing")+
        AtomicID::registerId(-1656,"CollectPropagate")+
        AtomicID::registerId(-1655,"AbandonPropagate")+
        AtomicID::registerId(-1149,"Ignore")+
        AtomicID::registerId(-1283,"MeqFunction")+
        TypeInfoReg::addToRegistry(-1283,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1283,__construct_MeqFunction)+
        AtomicID::registerId(-1336,"Delete")+
        AtomicID::registerId(-1482,"Debug")+
        AtomicID::registerId(-1537,"Enabled")+
        AtomicID::registerId(-1553,"Cwd")+
        AtomicID::registerId(-1723,"Append")+
        AtomicID::registerId(-1224,"File")+
        AtomicID::registerId(-1054,"Timestamp")+
        AtomicID::registerId(-1704,"MeqSpline")+
        TypeInfoReg::addToRegistry(-1704,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1704,__construct_MeqSpline)+
    0;
    return res;
  }
  
  int __dum_call_registries_for_Meq = aidRegistry_Meq();

