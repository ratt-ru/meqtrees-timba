//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

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
  //cout<<"dbtype"<<dbtype<<" name "<<dbname<<" new "<<forceNew<<endl;
  
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




  LOFAR::ParmDB::ParmValueSet result; 
  try{
    result = thisDB->getValues(parmName,parmDomain,parentId,LOFAR::ParmDB::ParmDBRep::UseNormal);  
  }
  catch(...)
    {
      cout<<"an Exception occured while getting values for parm "<<parmName<<endl;
      Py_INCREF(Py_None);
      return Py_None;
      
    }

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
  LOFAR::ParmDB::ParmValueSet result;
  try{
   result = thisDB->getValues(parmName,parmDomain,parentId,LOFAR::ParmDB::ParmDBRep::UseNormal);
  }
  catch(...)
    {
      cout<<"an Exception occured while getting all values for parm "<<parmName<<endl;
      Py_INCREF(Py_None);
      return Py_None;
      
    }

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
  vector<string> result;
  try{
    result = thisDB->getNames(pattern,LOFAR::ParmDB::ParmDBRep::UseNormal);  
  }
  catch(...)
    {
      cout<<"an Exception occured while getting names from parmtable "<<endl;
      Py_INCREF(Py_None);
      return Py_None;
      
    }


  PyObject * nameList=PyList_New(result.size());
  int i=0;
  for(vector<string>::iterator pvIt=result.begin(); pvIt!=result.end();pvIt++){
    
    PyList_SetItem(nameList,i++,Py_BuildValue("s",(*pvIt).c_str()));
  } 
  
  
  return nameList;
  
}

static PyObject * GetRange_wrapper(PyObject *pSelf,
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
  LOFAR::ParmDB::ParmDomain result;
  try
    {
      result = thisDB->getRange(pattern);  
    }
  catch(...)
    {
      cout<<"an Exception occured while getting range for parms: "<<pattern<<endl;
      Py_INCREF(Py_None);
      return Py_None;
      
    }
  
  Meq::Domain resultdomain = MeqfromParmDomain(result);

  return OctoPython::pyFromDMI(resultdomain);
  
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
    { "getRange", GetRange_wrapper, METH_VARARGS,
      "getrange from db following namepattern" },
    { NULL, NULL, 0, NULL}        /* Sentinel */

};

PyMODINIT_FUNC
initpyparmdb(void)
{
    (void) Py_InitModule("pyparmdb", TableMethods);
}

