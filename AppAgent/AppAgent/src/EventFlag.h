#ifndef APPAGENT_SRC_APPEVENTFLAG_H_HEADER_INCLUDED_EC72D1EB
#define APPAGENT_SRC_APPEVENTFLAG_H_HEADER_INCLUDED_EC72D1EB
    
#include <Common/Thread/Condition.h>
#include <DMI/CountedRef.h>

namespace AppAgent
{    
using namespace DMI;

//##ModelId=3E43E34D0342
class EventFlag : public SingularRefTarget
{
  public:
    //##ModelId=3E43E49702A5
    EventFlag();
    //##ModelId=3E43E49702AE
    EventFlag(const EventFlag& right);
    //##ModelId=3E43E49702D4
    EventFlag& operator=(const EventFlag& right);

    //##ModelId=3E43EDCD037F
    int addSource (bool is_async = false);

    //##ModelId=3E43E440007D
    void raise (int snum);
    //##ModelId=3E43EA3D0366
    void clear (int snum);

    //##ModelId=3E43E42300F1
    // waits until flag is raised
    // If lock=true, locks mutex() itself to check flag
    // If lock=false, assumes caller has a lock on the mutex and does nothing
    bool wait (bool lock=true) const
    { return wait(FULLMASK,lock); }
    
    // waits until flag for specific sources is raised. Mask should be
    // a combination of masks returned by sourceMask().
    // If lock=true, locks mutex() itself to check flag
    // If lock=false, assumes caller has a lock on the mutex and does nothing
    bool wait (ulong mask,bool lock) const;
    
    // waits for any signal on the flag, does not check if anything is raised
    void waitAny (bool lock=true);
    
    static ulong sourceMask (int snum) 
    { return 1<<snum; }
    
    // returns internal condition variable, by reference. Useful if a thread
    // wants to wait on the event flag without checking for specific bits
    Thread::Condition & condVar ()
    { return cond; }
    
    //##ModelId=3E43E88B02ED
    typedef CountedRef<EventFlag> Ref;
    
    //##ModelId=3E477BBC03A2
    bool isRaised() const;

  private:
    //##ModelId=3E43E4150343
    Thread::Condition cond;

    //##ModelId=3E43E4330050
    ulong flagword;
    //##ModelId=3E477A5E00B7
    int nsources;
    //##ModelId=3E477A5E00E7
    // use a 32-bit source mask
    static const int MAXSOURCES = 32;
    
    static const ulong FULLMASK = 0xFFFFFFFF;
    
    //##ModelId=3E43E84A01F0
    bool have_async;

};

//##ModelId=3E477BBC03A2
inline bool EventFlag::isRaised () const
{
  return flagword != 0;
}


};
#endif /* APPAGENT_SRC_APPEVENTFLAG_H_HEADER_INCLUDED_EC72D1EB */
