#ifndef VisCube_VisCube_h
#define VisCube_VisCube_h 1
    
#include "config.h"
    
#include "Common/Debug.h"

#include "DMI/TypeInfo.h"
    
 // for now (remove once lofarconf option is available)
#define HAVE_BLITZ 1
// Until I convert DMI to Lorrays, this must be included last to insure 
// correct definition of DoForAllArrayTypes, etc. 
#include "Common/Lorrays.h"
    
class VisCubeDebugContext 
{
  LocalDebugContext;
};
    
#endif
