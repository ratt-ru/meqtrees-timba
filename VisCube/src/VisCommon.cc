#include "VisCube/VisCommon.h"
#include "VisCube/TID-VisCube.h"
    
// make sure registry is puled in
static int dum = aidRegistry_VisCube();    
    
// init the debug context
InitDebugContext(VisCubeDebugContext,"VisCube");
