#ifndef OCTOGlish_GlishUtil_h
#define OCTOGlish_GlishUtil_h 1

#include <DMI/DMI.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
    
#include <aips/Glish.h>

namespace GlishUtil
{
  class GlishUtilDebugContext
  {
    public: LocalDebugContext;
  };
  
  ImportDebugContext(GlishUtilDebugContext);
  
  GlishArray makeFailField ( const String &msg );

  bool makeGlishArray (GlishArray &arr,const NestableContainer &nc,TypeId tid,bool adjustIndex);
    
  GlishRecord recToGlish (const DataRecord &rec);

  GlishValue objectToGlishValue (const BlockableObject &obj,bool adjustIndex);

  ObjRef makeDataArray (const GlishArray &arr,bool adjustIndex);

  void makeDataField (DataField &field,const GlishArray &arr,bool adjustIndex);

      
  ObjRef glishValueToObject (const GlishValue &val,bool adjustIndex);

  GlishRecord objectToBlockRec (const BlockableObject &obj);

  BlockableObject * blockRecToObject (const GlishRecord &rec);

  template<class T> 
  void initDataField (DataField &field,const GlishArray &arr);
  
  template<class T> 
  void newDataArray (ObjRef &ref,const GlishArray &arr);
  
  template<class Base>
  Base * GlishUtil::createSubclass (ObjRef &ref,const GlishValue &val);
}
#endif
