#ifndef APPAGENT_SRC_BOIOSINK_H_HEADER_INCLUDED_D0F0C734
#define APPAGENT_SRC_BOIOSINK_H_HEADER_INCLUDED_D0F0C734
    
#include <AppAgent/AppEventSink.h>
#include <AppAgent/AID-AppAgent.h>
#include <DMI/BOIO.h>
#include <DMI/HIID.h>
    
#pragma aid BOIO File Name Mode Event Data
    
namespace AppEvent
{
  const HIID
              FBOIOFile   = AidBOIO|AidFile|AidName,
              FBOIOMode   = AidBOIO|AidFile|AidMode;
};
    

//##ModelId=3E53C56B02DD
class BOIOSink : public AppEventSink
{
  public:
    //##ModelId=3E54E81503BF
    BOIOSink ()
      : AppEventSink(HIID()) {}
      
    //##ModelId=3E53C59D00EB
    //##Documentation
    virtual bool init(const DataRecord &data);

    //##ModelId=3E53C5A401E1
    //##Documentation
    virtual void close();

    //##ModelId=3E53C5B401CB
    //##Documentation
    virtual int getEvent(HIID &id, ObjRef &data, const HIID &mask, int wait = AppEvent::WAIT);

    //##ModelId=3E53C5BB0014
    //##Documentation
    virtual int hasEvent(const HIID &mask = HIID()) const;

    //##ModelId=3E53C5C2003E
    //##Documentation
    //## Posts an event on behalf of the application.
    virtual void postEvent(const HIID &id, const ObjRef::Xfer &data = ObjRef());

    //##ModelId=3E53C5CE0339
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E54E815039B
    LocalDebugContext;

  private:
    //##ModelId=3E54BD23023F
    mutable BOIO boio;
  
    //##ModelId=3E54BD6D02DD
    mutable bool cached_event;
    //##ModelId=3E54BD74016B
    mutable HIID cached_id;
    //##ModelId=3E54BD78018D
    mutable ObjRef cached_data;

};

#endif /* APPAGENT_SRC_BOIOSINK_H_HEADER_INCLUDED_D0F0C734 */
