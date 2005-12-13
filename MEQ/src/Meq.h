#ifndef MEQ_MEQ_H
#define MEQ_MEQ_H

#include <Common/Debug.h>
#include <Common/Thread/Mutex.h>
#include <DMI/DMI.h>
#include <DMI/Exception.h>
    
namespace DebugMeq
{
  extern ::Debug::Context DebugContext;
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
}

namespace Meq
{
  using namespace DMI;
  
  // AIPS++ is not thread-safe, so we protect components with a mutex
  extern Thread::Mutex aipspp_mutex;

  //## These exception are meant to be thrown from methods like Node::init(),
  //## getResult(), processCommands() and setStateImpl() when something goes 
  //## wrong. The type of the exception indicates whether any cleanup is 
  //## required.
  
  class FailWithCleanup : public ExceptionList
  {
    public:
      FailWithCleanup(const std::string& text,
                      const std::string& file="",int line=0,
                      const std::string& func="")
      : ExceptionList(Elem(text,file,line,func))
      {}

      FailWithCleanup(const std::string& text,const std::string &object,
                      const std::string& file="",int line=0,
                      const std::string& func="")
      : ExceptionList(Elem(text,object,file,line,func))
      {}
        
  };
  
  class FailWithoutCleanup : public ExceptionList
  {
    public:
      FailWithoutCleanup(const std::string& text,
                         const std::string& file="",int line=0,
                         const std::string& func="")
      : ExceptionList(Elem(text,file,line,func))
      {}

      FailWithoutCleanup(const std::string& text,const std::string &object,
           const std::string& file="",int line=0,
           const std::string& func="")
      : ExceptionList(Elem(text,object,file,line,func))
      {}
        
  };
  
      
}

#endif
