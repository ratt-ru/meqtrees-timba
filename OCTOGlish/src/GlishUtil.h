#ifndef OCTOGlish_GlishUtil_h
#define OCTOGlish_GlishUtil_h 1

#include <Common/Debug.h>
#include <DMI/DMI.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
    
#include <aips/Glish.h>

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
  
  GlishArray makeFailField ( const String &msg );

  bool makeGlishArray (GlishArray &arr,const NestableContainer &nc,TypeId tid,bool adjustIndex);
    
  GlishRecord recToGlish (const DataRecord &rec);

  GlishValue objectToGlishValue (const BlockableObject &obj,bool adjustIndex);

  ObjRef makeDataArray (const GlishArray &arr,bool adjustIndex);

  void makeDataField (DataField &field,const GlishArray &arr,bool adjustIndex,bool isScalar);
      
  ObjRef glishValueToObject (const GlishValue &val,bool adjustIndex);

  GlishRecord objectToBlockRec (const BlockableObject &obj);

  BlockableObject * blockRecToObject (const GlishRecord &rec);

  template<class T> 
  void initDataField (DataField &field,const GlishArray &arr,bool isScalar);
  
  template<class T> 
  void newDataArray (ObjRef &ref,const GlishArray &arr);
  
  template<class Base>
  Base * GlishUtil::createSubclass (ObjRef &ref,const GlishValue &val);
}
#endif
