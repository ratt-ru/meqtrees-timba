#ifndef OCTOPROXYWP_H_HEADER_INCLUDED_C75F583E
#define OCTOPROXYWP_H_HEADER_INCLUDED_C75F583E
#include "WorkProcess.h"
#include "Message.h"

namespace Octoproxy {

//##ModelId=3E08FF0D035E
class ProxyWP : public WorkProcess
{
  public:
    //##ModelId=3E08FFD30196
    ProxyWP(AtomicID wpid);
  
  
  protected:

  private:

    //##ModelId=3E08FF12002C
    ProxyWP();

    //##ModelId=3E08FF120032
    ProxyWP& operator=(const ProxyWP& right);
    //##ModelId=3E08FF12002E
    ProxyWP(const ProxyWP& right);


};

} // namespace Octoproxy



#endif /* OCTOPROXYWP_H_HEADER_INCLUDED_C75F583E */
