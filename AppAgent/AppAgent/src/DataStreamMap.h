#ifndef _AppAgent_DataStreamMap_h 
#define _AppAgent_DataStreamMap_h 1
    
#include <Common/Thread.h>
#include <DMI/HIID.h>
#include <DMI/TypeId.h>
#include <map>
    
namespace AppAgent
{    
using namespace DMI;

//##ModelId=3EB242510253
class DataStreamMap
{
  public:
    //##ModelId=3EB2425102CE
    typedef struct 
    { 
      int    code;
      HIID   eventmask;
      TypeId datatype;
      bool   data_required;
    } Entry;
    
    //##ModelId=3EB242EC03D7
    DataStreamMap ();
    
    //##ModelId=3EB242EC03D8
    bool isInitialized (Thread::Mutex::Lock &lock);
    
    //##ModelId=3EB242EC03DC
    void initialize ();
    
    //##ModelId=3EB242EC03E1
    DataStreamMap & add (int code,const HIID &evmask,TypeId type,bool required);
        
    //##ModelId=3EB242ED0010
    const Entry & find (int code) const;

    //##ModelId=3EB242ED0025
    const HIID & eventMask () const;

  private:
    //##ModelId=3EB242ED002B
    DataStreamMap (const DataStreamMap &other);
    //##ModelId=3EB242ED0039
    void operator = (const DataStreamMap &other);
      
    //##ModelId=3EB242EC037A
    std::map<int,Entry>  codemap;

    //##ModelId=3EB242EC03B9
    static Entry _dum;
    
    //##ModelId=3EB242EC03C2
    Thread::Mutex mutex;
    //##ModelId=3EB242EC03CA
    bool initialized;
};

};
#endif
