#include "DMI.h"
#include "AID-DMI.h"
#include "Allocators.h"
    
namespace DebugDMI
{
  ::Debug::Context DebugContext("DMI");
};

int DMI::initialize ()
{
  return aidRegistry_DMI();
}

