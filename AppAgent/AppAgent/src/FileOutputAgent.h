#ifndef VISAGENT_SRC_VISFILEOUTPUTAGENT_H_HEADER_INCLUDED_C26B922B
#define VISAGENT_SRC_VISFILEOUTPUTAGENT_H_HEADER_INCLUDED_C26B922B
    
#include <AppAgent/FileAgentBase.h>
#include <AppAgent/OutputAgent.h>

namespace AppAgent
{    
namespace VisAgent 
{

//##ModelId=3E02FF13009E
class FileOutputAgent : public OutputAgent, public FileAgentBase
{
  public:
    //##ModelId=3E2C29B00086
    //##Documentation
    //## Reports current state of agent. Default version always reports success
    virtual int state() const;

    //##ModelId=3E2C29B40120
    //##Documentation
    //## Reports current state as a string
    virtual string stateString() const;
    
  protected:
    //##ModelId=3E42409400DB
    FileOutputAgent (const HIID &initf)
      : OutputAgent(initf) {}

  private:
    //##ModelId=3E42409402CF
    FileOutputAgent();
    //##ModelId=3E42466D02E5
    FileOutputAgent(const FileOutputAgent& right);
    //##ModelId=3E42409403BA
    FileOutputAgent& operator=(const FileOutputAgent& right);

};


} // namespace VisAgent

};


#endif /* VISAGENT_SRC_VISFILEOUTPUTAGENT_H_HEADER_INCLUDED_C26B922B */
