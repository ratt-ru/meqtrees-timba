#ifndef VCube_VCube_h
#define VCube_VCube_h 1
    
#include "config.h"
#include <TimBase/Debug.h>
#include <DMI/TypeInfo.h>

// OMS 04/01/2005: time to get rid of this?    
// // for now (remove once lofarconf option is available)
//#define HAVE_BLITZ 1
//// Until I convert DMI to Lorrays, this must be included last to insure 
//// correct definition of DoForAllArrayTypes, etc. 
//#include "TimBase/Lorrays.h"

namespace VisCube 
{
using namespace DMI;
    
class VisCubeDebugContext 
{
  public: LocalDebugContext;
};
    
#endif

};
