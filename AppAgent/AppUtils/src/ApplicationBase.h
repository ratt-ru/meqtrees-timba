#ifndef APPUTILS_APPLICATIONBASE_H_HEADER_INCLUDED_D448A9D9
#define APPUTILS_APPLICATIONBASE_H_HEADER_INCLUDED_D448A9D9

#include <Common/Thread.h>    
#include <Common/Thread/Mutex.h>    
#include <DMI/DataRecord.h>    
#include <AppAgent/AppControlAgent.h>
#include <VisAgent/InputAgent.h>
#include <VisAgent/OutputAgent.h>
#include <AppUtils/AID-AppUtils.h>
    
#include <string>
#include <list>
using std::string;
    
#pragma aidgroup AppUtils
#pragma aid Input Output Seq Error Closed Init Fail
    

namespace ApplicationVocabulary
{
  const HIID
      InputClosedEvent    = AidInput|AidClosed,
      InputErrorEvent     = AidInput|AidError,
      
      OutputErrorEvent    = AidOutput|AidError,
      OutputSequenceEvent = AidOutput|AidSeq|AidError,
  
      InputInitFailed     = AidInput|AidInit|AidFail,
      OutputInitFailed    = AidOutput|AidInit|AidFail;
};

//##ModelId=3E3FE1770336
class ApplicationBase : public SingularRefTarget
{
  private:
    //##ModelId=3E3FE29D0372
    Thread::ThrID thread_;
    //##ModelId=3E3FE2A70351
    mutable Thread::Mutex mutex_;
    //##ModelId=3E43B89C0135
    AppControlAgent * control_;
    
  
  public:
  
    //##ModelId=3E3FE7660131
    virtual ~ApplicationBase();

    //##ModelId=3E3FE1B8005F
    virtual void run () = 0;

    //##ModelId=3E3FE1C8036D
    virtual int state () const;

    //##ModelId=3E3FE1CD009F
    virtual string stateString () const;

    //##ModelId=3E7894E90398
    virtual bool verifySetup (bool throw_exc = False) const;
    
    //##ModelId=3E3FE1BB0220
    Thread::ThrID runThread (bool del_on_exit = True);

    //##ModelId=3E3FE532001B
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E3FE5C50066
    const char *debug(int detail = 1, const string &prefix = "", const char *name = 0) const
    { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
    
    //##ModelId=3E3FE1DA000B
    Thread::Mutex &mutex () const              { return mutex_; }
    //##ModelId=3E3FE30803E1
    Thread::ThrID thread () const              { return thread_; } 
    //##ModelId=3E43BA79039A
    AppControlAgent & control ()               { return *control_; }
    //##ModelId=3E6F6015009E
    const AppControlAgent & control () const   { return *control_; }
    //##ModelId=3E78940001D6
    bool hasControlAgent () const              { return control_ != 0; }
    
    //##ModelId=3E77212C02CD
    virtual void attach (AppControlAgent *ctrl, int flags);
    //##ModelId=3E7721560344
    virtual void attach (VisAgent::InputAgent *inp, int flags);
    //##ModelId=3E7721810096
    virtual void attach (VisAgent::OutputAgent *outp, int flags);

    
    //##ModelId=3E77214903A2
    ApplicationBase & operator << (AppControlAgent &ctrl)
    { attach(&ctrl,DMI::WRITE|DMI::EXTERNAL); return *this; }
    //##ModelId=3E77219B005A
    ApplicationBase & operator << (VisAgent::InputAgent &inp)
    { attach(&inp,DMI::WRITE|DMI::EXTERNAL); return *this; }
    //##ModelId=3E7721B103B3
    ApplicationBase & operator << (VisAgent::OutputAgent &outp)
    { attach(&outp,DMI::WRITE|DMI::EXTERNAL); return *this; }
    
    //##ModelId=3E77245E016D
    ApplicationBase & operator << (AppControlAgent *ctrl)
    { attach(ctrl,DMI::ANONWR); return *this; }
    //##ModelId=3E77245E02ED
    ApplicationBase & operator << (VisAgent::InputAgent *inp)
    { attach(inp,DMI::ANONWR); return *this; }
    //##ModelId=3E77245F0059
    ApplicationBase & operator << (VisAgent::OutputAgent *outp)
    { attach(outp,DMI::ANONWR); return *this; }

    //##ModelId=3E7893B10086
    DefineRefTypes(ApplicationBase,Ref);

    
    //##ModelId=3E3FEDBE0291
    LocalDebugContext;
    
  protected:
    //##ModelId=3E3FE4020002
    ApplicationBase();
    //##ModelId=3E7722D50064
    void attachRef(AppAgent::Ref::Xfer & agent);


  private:
    //##ModelId=3E43BBE301BA
    ApplicationBase (const ApplicationBase& right);
    //##ModelId=3E43BBE302A3
    ApplicationBase& operator=(const ApplicationBase& right);
    
    //##ModelId=3E3FE1DD017A
    static void *startThread (void *arg);

    void do_run ();
    
    //##ModelId=3E43BBE202DA
    bool delete_on_exit;

    //##ModelId=3E43B9080057
    std::list<AppAgent::Ref> agentrefs_;
};

#endif /* APPLICATIONBASE_H_HEADER_INCLUDED_D448A9D9 */
