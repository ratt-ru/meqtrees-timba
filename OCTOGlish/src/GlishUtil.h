#ifndef OCTOGlish_GlishUtil_h
#define OCTOGlish_GlishUtil_h 1

#include <Common/Debug.h>
#include <DMI/DMI.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
    
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

  bool makeGlishArray (casa::GlishArray &arr,const NestableContainer &nc,TypeId tid,bool adjustIndex);
    
  casa::GlishRecord recToGlish (const DataRecord &rec);

  casa::GlishValue objectToGlishValue (const BlockableObject &obj,bool adjustIndex);

  ObjRef makeDataArray (const casa::GlishArray &arr,bool adjustIndex);

  void makeDataField (DataField &field,const casa::GlishArray &arr,bool adjustIndex,bool isScalar);
      
  ObjRef glishValueToObject (const casa::GlishValue &val,bool adjustIndex);

  casa::GlishRecord objectToBlockRec (const BlockableObject &obj);

  BlockableObject * blockRecToObject (const casa::GlishRecord &rec);

  template<class T> 
  void initDataField (DataField &field,const casa::GlishArray &arr,bool isScalar);
  
  template<class T> 
  void newDataArray (ObjRef &ref,const casa::GlishArray &arr);
  
  template<class Base>
  Base * createSubclass (ObjRef &ref,const casa::GlishValue &val);
}
#endif
