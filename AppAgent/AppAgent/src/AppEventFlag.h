#ifndef APPAGENT_SRC_APPEVENTFLAG_H_HEADER_INCLUDED_EC72D1EB
#define APPAGENT_SRC_APPEVENTFLAG_H_HEADER_INCLUDED_EC72D1EB
    
#include <Common/Thread/Condition.h>
#include <DMI/CountedRef.h>

//##ModelId=3E43E34D0342
class AppEventFlag : public SingularRefTarget
{
  public:
    //##ModelId=3E43E49702A5
    AppEventFlag();
    //##ModelId=3E43E49702AE
    AppEventFlag(const AppEventFlag& right);
    //##ModelId=3E43E49702D4
    AppEventFlag& operator=(const AppEventFlag& right);

    //##ModelId=3E43EDCD037F
    int addSource (bool is_async = False);

    //##ModelId=3E43E440007D
    void raise (int snum);
    //##ModelId=3E43EA3D0366
    void clear (int snum);

    //##ModelId=3E43E42300F1
    bool wait() const;
    
    //##ModelId=3E43E88B02ED
    DefineRefTypes(AppEventFlag,Ref);
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
    
    //##ModelId=3E43E84A01F0
    bool have_async;

};

//##ModelId=3E477BBC03A2
inline bool AppEventFlag::isRaised () const
{
  return flagword != 0;
}



#endif /* APPAGENT_SRC_APPEVENTFLAG_H_HEADER_INCLUDED_EC72D1EB */
