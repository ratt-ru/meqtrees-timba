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
}

#endif
