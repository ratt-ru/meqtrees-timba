#ifndef APPAGENT_SRC_BOIOSINK_H_HEADER_INCLUDED_D0F0C734
#define APPAGENT_SRC_BOIOSINK_H_HEADER_INCLUDED_D0F0C734
    
#include <AppAgent/FileSink.h>
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
class BOIOSink : public FileSink
{
  public:
    //##ModelId=3E54E81503BF
    BOIOSink ()
      : FileSink() {}
      
    //##ModelId=3E53C59D00EB
    //##Documentation
    virtual bool init(const DataRecord &data);

    //##ModelId=3E53C5A401E1
    //##Documentation
    virtual void close();

    //##ModelId=3E53C5C2003E
    //##Documentation
    //## Posts an event on behalf of the application.
    virtual void postEvent(const HIID &id, const ObjRef::Xfer &data = ObjRef());
    //##ModelId=3E8C252801E8
    //##Documentation
    //## Checks whether a specific event is bound to any output. Always returns
    //## True, since all BOIO events are bound to the file.
    virtual bool isEventBound(const HIID &id);

    //##ModelId=3E53C5CE0339
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3E54E815039B
    LocalDebugContext;
    
  protected:
    //##ModelId=3EC23EF30079
    virtual int refillStream();

  private:
    //##ModelId=3E54BD23023F
    mutable BOIO boio;
  
};

#endif /* APPAGENT_SRC_BOIOSINK_H_HEADER_INCLUDED_D0F0C734 */
