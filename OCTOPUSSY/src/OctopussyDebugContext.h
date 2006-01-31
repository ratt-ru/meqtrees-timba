#ifndef OCTOPUSSY_OctopussyDebugContext_h
#define OCTOPUSSY_OctopussyDebugContext_h 1

#include <TimBase/Debug.h>

namespace DebugOctopussy
{
  extern ::Debug::Context DebugContext;
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
}
    
namespace Octopussy
{

//##ModelId=3C7FA3020068
class OctopussyDebugContext 
{
  public:
    //##ModelId=3DB936CC02B0
    ImportDebugContext(DebugOctopussy);
};

// Class OctopussyDebugContext 

};

#endif
