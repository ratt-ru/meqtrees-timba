#ifndef OCTOAGENT_SRC_EVENTMULTIPLEXER_H_HEADER_INCLUDED_B481AF8F
#define OCTOAGENT_SRC_EVENTMULTIPLEXER_H_HEADER_INCLUDED_B481AF8F
    
#include <OCTOPUSSY/Message.h>
#include <OCTOPUSSY/WorkProcess.h>
#include <AppAgent/OctoEventSink.h>
    
namespace AppAgent
{    

class AppEventFlag;

namespace OctoAgent    
{
using namespace Octopussy;
    
//##ModelId=3E26BABA0069
class EventMultiplexer : public WorkProcess
{
  public:
      
    //##ModelId=3E26BE240137
    explicit EventMultiplexer (AtomicID wpid);
  
    //##ModelId=3E26BE670240
    virtual ~EventMultiplexer ();
  
    //##ModelId=3E50F5040362
    AppEventFlag & eventFlag();
    
    //##ModelId=3E535889025A
    EventSink & newSink ();

    //##ModelId=3E428F93013E
    EventMultiplexer& addSink  (EventSink::Ref &sink);
    //##ModelId=3E26BE760036
    EventMultiplexer&  addSink (EventSink* sink,int flags = DMI::ANONWR);
    //##ModelId=3E428F70021D
    EventMultiplexer&  addSink (EventSink& sink,int flags = DMI::WRITE);
    
    //##ModelId=3E428F7002D6
    EventMultiplexer&  operator <<= (EventSink* sink)
    { return addSink(sink,DMI::ANONWR); }
    //##ModelId=3E428F700392
    EventMultiplexer&  operator <<= (EventSink& sink)
    { return addSink(sink,DMI::ANONWR); }
    
    //##ModelId=3E50E02C024B
    void init();
    //##ModelId=3E50E292002B
    void close();
    
    //##ModelId=3E26D2D6021D
    int   getEvent (HIID& id,ObjRef& data,const HIID& mask,int wait,
                    HIID &source,int sink_id);
    //##ModelId=3E3FC3A601B0
    int   hasEvent (const HIID& mask,int sink_id);
    
    //##ModelId=3E26E30E01C5
    string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E26E70701D5
    const char * debug ( int detail = 1,const string &prefix = "",
                         const char *name = 0 ) const
    { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

    //##ModelId=3E53599A0049
    LocalDebugContext;
    
    //##ModelId=3E9BD63F0297
    DefineRefTypes(EventMultiplexer,Ref);
    
  protected:
    //##ModelId=3E47C84502CD
    virtual void notify ();
    //##ModelId=3E47CFA70203
    virtual void stop();


  private:
    //##ModelId=3E26BE6701CD
    EventMultiplexer (const EventMultiplexer& right);
    //##ModelId=3E26BE670273
    EventMultiplexer& operator=(const EventMultiplexer& right);
    //##ModelId=3E428FC40127
    EventMultiplexer();
      
    //##ModelId=3E3FC3A7000B
    int checkQueue (const HIID& mask,int wait,int sink_id);

    //##ModelId=3E428C4D0239
    std::vector<EventSink::Ref> sinks;
    //##ModelId=3E3FC3A50362
    int assigned_sink;
    //##ModelId=3E3FC3A6004B
    HIID assigned_event;
    //##ModelId=3F5F4364023A
    HIID assigned_source;
    //##ModelId=3E50E2D3025D
    ObjRef assigned_data;
    //##ModelId=3E50E2D801A4
    const Message * pheadmsg;
    
    //##ModelId=3E47C785025B
    AppEventFlag::Ref eventFlag_;
    //##ModelId=3E47BE2D0131
    int ef_sink_num;
};

//##ModelId=3E50F5040362
inline AppEventFlag & EventMultiplexer::eventFlag()
{
  return eventFlag_.dewr();
}

} // namespace OctoAgent    

};

#endif /* OCTOAGENT_SRC_OCTOMULTIPLEXER_H_HEADER_INCLUDED_B481AF8F */
