#ifndef OCTOGlish_GlishUtil_h
#define OCTOGlish_GlishUtil_h 1

#include <TimBase/Debug.h>
#include <DMI/DMI.h>
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>
    
#include <tasking/Glish.h>

namespace GlishUtil
{
//##ModelId=400E516F03A3
  class GlishUtilDebugContext
  {
    public:
    //##ModelId=400E516F03D8
    LocalDebugContext;
  };
  
  ImportDebugContext(GlishUtilDebugContext);
  
  casa::GlishArray makeFailField ( const casa::String &msg );
  casa::GlishArray makeMissingValue ();
  casa::GlishArray GlishUtil::makeEmptyObject (DMI::TypeId tid);

  bool makeGlishArray (casa::GlishArray &arr,const DMI::Container &nc,DMI::TypeId tid,bool adjustIndex);
    
  casa::GlishRecord recToGlish (const DMI::Record &rec);

  casa::GlishValue objectToGlishValue (const DMI::BObj &obj,bool adjustIndex);

  DMI::ObjRef makeDMINumArray (const casa::GlishArray &arr,bool adjustIndex);

  void makeDMIVec (DMI::Vec &field,const casa::GlishArray &arr,bool adjustIndex,bool isScalar);
      
  DMI::ObjRef glishValueToObject (const casa::GlishValue &val,bool adjustIndex);

  casa::GlishRecord objectToBlockRec (const DMI::BObj &obj);

  DMI::ObjRef blockRecToObject (const casa::GlishRecord &rec);

  template<class T> 
  void initDMIVec (DMI::Vec &field,const casa::GlishArray &arr,bool isScalar);
  
  template<class T> 
  void newDMINumArray (DMI::ObjRef &ref,const casa::GlishArray &arr);
  
  template<class Base>
  Base * createSubclass (DMI::ObjRef &ref,const casa::GlishValue &val);
};
#endif
