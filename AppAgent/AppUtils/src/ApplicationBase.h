#ifndef APPUTILS_APPLICATIONBASE_H_HEADER_INCLUDED_D448A9D9
#define APPUTILS_APPLICATIONBASE_H_HEADER_INCLUDED_D448A9D9

#include <Common/Thread.h>    
#include <Common/Thread/Mutex.h>    
#include <DMI/DataRecord.h>    
#include <AppAgent/AppControlAgent.h>
    
#include <string>
    
using std::string;

//##ModelId=3E3FE1770336
class ApplicationBase
{
  private:
    //##ModelId=3E3FE29D0372
    Thread::ThrID thread_;
    //##ModelId=3E3FE2A70351
    mutable Thread::Mutex mutex_;
    //##ModelId=3E43B89C0135
    AppControlAgent & control_;
    
  
  public:
  
    //##ModelId=3E3FE7660131
    virtual ~ApplicationBase();

    //##ModelId=3E3FE1B8005F
    virtual void run (DataRecord::Ref &initrec) = 0;

    //##ModelId=3E3FE1C8036D
    virtual int state () const;

    //##ModelId=3E3FE1CD009F
    virtual string stateString () const;


    //##ModelId=3E3FE1BB0220
    Thread::ThrID runThread (DataRecord::Ref &initrec,bool del_on_exit = True);

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
    AppControlAgent & control ()               { return control_; }
    //##ModelId=3E43BA79039A
    const AppControlAgent & control () const   { return control_; }

    //##ModelId=3E3FEDBE0291
    LocalDebugContext;
    
  protected:
    //##ModelId=3E3FE4020002
    ApplicationBase(AppControlAgent &ctrl);

  private:
    //##ModelId=3E43BBE301BA
    ApplicationBase (const ApplicationBase& right);
    //##ModelId=3E43BBE302A3
    ApplicationBase& operator=(const ApplicationBase& right);
    
    //##ModelId=3E3FE1DD017A
    static void *startThread (void *arg);

    //##ModelId=3E3FE1F40325
    DataRecord::Ref initrec_cache;
    
    //##ModelId=3E43BBE202DA
    bool delete_on_exit;

    //##ModelId=3E43B9080057
    AppAgent::Ref controlref_;
};

#endif /* APPLICATIONBASE_H_HEADER_INCLUDED_D448A9D9 */
