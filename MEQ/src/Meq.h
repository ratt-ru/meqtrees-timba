#ifndef MEQ_MEQ_H
#define MEQ_MEQ_H

#include <Common/Debug.h>
#include <DMI/DMI.h>
    
namespace DebugMeq
{
  extern ::Debug::Context DebugContext;
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
}

namespace Meq
{
  using namespace DMI;
  
  //## These exception are meant to be thrown from methods like Node::init(),
  //## getResult(), processCommands() and setStateImpl() when something goes 
  //## wrong. The type of the exception indicates whether any cleanup is 
  //## required.
  EXCEPTION_CLASS(FailWithCleanup,LOFAR::Exception)
  EXCEPTION_CLASS(FailWithoutCleanup,LOFAR::Exception)
      
}

#endif
