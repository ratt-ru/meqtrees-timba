#include "Python.h"
#include "ParmDB/ParmDBMeta.h"
#include "ParmDB/ParmDB.h"
#include "ParmDB/ParmValue.h"
#include "MEQ/Funklet.h"
#include "MEQ/Domain.h"
#include "MEQ/Axis.h"

#include <iostream>


#include "DMI/BObj.h"
#include "OCTOPython/OctoPython.h"
using namespace std;
using namespace LOFAR::ParmDB;

#ifdef HAVE_PARMDB

Meq::Domain::Ref MeqfromParmDomain(const ParmDomain & pdom){
  const std::vector<double> start=pdom.getStart();
  const std::vector<double> end= pdom.getEnd();
  Meq::Domain::Ref domref;
  
  domref<<=  new Meq::Domain(start[0],end[0],start[1],end[1]);
  for(uint iaxis =2;iaxis<start.size();iaxis++)
    domref().defineAxis(iaxis,start[iaxis],end[iaxis]); 
  return domref;
}

ParmDomain MeqtoParmDomain(const Meq::Domain::Ref domref){
  std::vector<double> start;
  std::vector<double> end;
  for(int iaxis =0;iaxis<Meq::Axis::MaxAxis;iaxis++)
    
    if(domref-> isDefined (iaxis))
      {
	start.push_back(domref->start(iaxis));
	end.push_back(domref->end(iaxis));
	
      }
    else
      break;

  ParmDomain pdom(start,end);
  return pdom;
}


Meq::Funklet::Ref  ParmValueToFunklet(const ParmValue &pv){

  Meq::Funklet::Ref funkletref;
  string type=pv.rep().itsType;
  const int axis[] = { Meq::Axis::TIME,Meq::Axis::FREQ };
  vector<double> cf=pv.rep().itsCoeff;
  const vector<int> shape=pv.rep().itsShape;
  const int nx=(shape.size() && shape[0]>0?shape[0]:1);
  const int ny=(shape.size()>1 && shape[1]>0?shape[1]:1);
  double data[nx*ny];
  for(int i=0;i<nx*ny;i++){
  //convert
    int j=ny*(i%nx);//rownr
    j+=i/nx;//collumn nr;
    data[j]=cf[i];
  }
  const LoMat_double theCoeff(data,LoShape(nx,ny)); 
  double offset[]={pv.rep().itsOffset[0],pv.rep().itsOffset[1]};
  double scale[]={pv.rep().itsScale[0],pv.rep().itsScale[1]};

  // what about more dmensions??
  //implement (see: Meqto/fromParmdomain....)
  

  funkletref<<=new Meq::Funklet(2,axis,offset,scale,
				pv.rep().itsPerturbation,pv.rep().itsWeight,
				pv.rep().itsDBRowRef);


  funkletref().setCoeff(theCoeff);
  funkletref().setFunction(type);
  //  funkletref().setConstants(pv.rep().itsConstants );

 
  Meq::Domain domain = MeqfromParmDomain(pv.rep().itsDomain);
  funkletref().setDomain(domain);
  return funkletref;
}

static PyObject * ParmValueSet2py(const ParmValueSet *pvs){
  vector<ParmValue> pvV=pvs->getValues();
  PyObject * FunkList=PyList_New(pvV.size());
  int i=0;
  Meq::Funklet::Ref funkref;

  for( vector<ParmValue>::iterator pvIt=pvV.begin(); pvIt!=pvV.end(); pvIt++)
    {
      funkref<<= ParmValueToFunklet(*pvIt);
      PyList_SetItem(FunkList,i++,OctoPython::pyFromDMI(funkref));
    }
  return FunkList;


}






static void delParmDB(void *ptr)
{
    //cout<<"Called PyDelNumbers()\n"; //Good to see once
    LOFAR::ParmDB::ParmDB * oldnum = static_cast<LOFAR::ParmDB::ParmDB *>(ptr);
    delete oldnum;
    return;
}

static PyObject *ParmDB_wrapper(PyObject *pSelf,
				PyObject *pArgs)
{
  //First, extract the arguments from a Python tuple
  const char * dbname;
  const char * dbtype;
  int forceNew;
  int ok = PyArg_ParseTuple(pArgs,"ssi",&dbname,&dbtype,&forceNew);
  if(!ok) {
    //exception
    //include error handling
    return NULL;
  }
  //check if type is correct
  cout<<"dbtype"<<dbtype<<" name "<<dbname<<" new "<<forceNew<<endl;
  
  //Second, dynamically allocate a new object
  
  LOFAR::ParmDB::ParmDBMeta db(dbtype, dbname);
  LOFAR::ParmDB::ParmDB *newtable;
 try
  {
    newtable = new LOFAR::ParmDB::ParmDB(db,forceNew);
  }
 catch(...)
   {
     cout<<"an EXception occured while opening parmdb"<<endl;
     Py_INCREF(Py_None);
     return Py_None;

   }
   
  //Third, wrap the pointer as a "PyCObject" and
  // return that object to the interpreter
  return PyCObject_FromVoidPtr( newtable,delParmDB);
  
}




//getvalues from parmdb
//provide 3 functions, search on names(can always be patterns?? nope), search on domain, search on parentid

static PyObject *GetValues_wrapper(PyObject *pSelf,
			   PyObject *pArgs)
{

  PyObject *pyParmDB;

  char *parmName;
  PyObject * pyDomain;
  int parentId;
  int ok = PyArg_ParseTuple(pArgs,"OsOi",&pyParmDB,&parmName,&pyDomain,&parentId);
  if(!ok) {
    //exception
    return NULL;
  }
  
  // Convert the PyCObject to a void pointer:
  void * temp = PyCObject_AsVoidPtr(pyParmDB);
  // Cast the void pointer to a ParmDB pointer:
  LOFAR::ParmDB::ParmDB * thisDB = static_cast<LOFAR::ParmDB::ParmDB *>(temp);

  Meq::Domain::Ref domref;
  DMI::ObjRef ref;
  
  OctoPython::pyToDMI(ref,pyDomain);

  domref <<= ref;
  //convert to parmdomain

  LOFAR::ParmDB::ParmDomain parmDomain = MeqtoParmDomain(domref);




  LOFAR::ParmDB::ParmValueSet result = thisDB->getValues(parmName,parmDomain,parentId,LOFAR::ParmDB::ParmDBRep::UseNormal);  
  PyObject * funkletList = ParmValueSet2py(&result);
  return funkletList;

}
 

static PyObject *GetAllValues_wrapper(PyObject *pSelf,
			   PyObject *pArgs)
{//getall values, set domain to empty domain
  PyObject *pyParmDB;

  char *parmName;
  int parentId;
  int ok = PyArg_ParseTuple(pArgs,"Osi",&pyParmDB,&parmName,&parentId);
  if(!ok) {
    //exception
    return NULL;
  }
  
  // Convert the PyCObject to a void pointer:
  void * temp = PyCObject_AsVoidPtr(pyParmDB);
  // Cast the void pointer to a ParmDB pointer:
  LOFAR::ParmDB::ParmDB * thisDB = static_cast<LOFAR::ParmDB::ParmDB *>(temp);

  
  LOFAR::ParmDB::ParmDomain parmDomain;
  
  LOFAR::ParmDB::ParmValueSet result = thisDB->getValues(parmName,parmDomain,parentId,LOFAR::ParmDB::ParmDBRep::UseNormal);  
  PyObject * funkletList = ParmValueSet2py(&result);
  return funkletList;


}



static PyObject * GetNames_wrapper(PyObject *pSelf,
			   PyObject *pArgs)
{
  //  getnames from pattern, default=*

  PyObject *pyParmDB;

  char *pattern;
  int ok = PyArg_ParseTuple(pArgs,"Os",&pyParmDB,&pattern);
  if(!ok) {
    //exception
    return NULL;
  }
  
  // Convert the PyCObject to a void pointer:
  void * temp = PyCObject_AsVoidPtr(pyParmDB);
  // Cast the void pointer to a Numbers pointer:
  LOFAR::ParmDB::ParmDB * thisDB = static_cast<LOFAR::ParmDB::ParmDB *>(temp);
  cout<<"getting names with pattern: "<<pattern<<endl;

  vector<string> result = thisDB->getNames(pattern,LOFAR::ParmDB::ParmDBRep::UseNormal);  

  PyObject * nameList=PyList_New(result.size());
  int i=0;
  for(vector<string>::iterator pvIt=result.begin(); pvIt!=result.end();pvIt++){
    
    PyList_SetItem(nameList,i++,Py_BuildValue("s",(*pvIt).c_str()));
  } 
  
  
  return nameList;
  
}
 
#endif

static PyMethodDef TableMethods[] = {
    { "openParmDB", ParmDB_wrapper, METH_VARARGS,
      "opens a parm DB" },
    { "getNames", GetNames_wrapper, METH_VARARGS,
      "getnames from db following pattern" },
    { "getValues", GetValues_wrapper, METH_VARARGS,
      "getvalues from db following name + domain" },
    { "getAllValues", GetAllValues_wrapper, METH_VARARGS,
      "getvalues from db following name +infinite domain" },
    { NULL, NULL, 0, NULL}        /* Sentinel */

};

PyMODINIT_FUNC
initpyparmdb(void)
{
    (void) Py_InitModule("pyparmdb", TableMethods);
}

