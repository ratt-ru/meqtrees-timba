#include "FileOutputAgent.h"

namespace VisAgent
{
  
using namespace AppEvent;
    
//##ModelId=3E2C29B00086
int FileOutputAgent::state() const
{
  return fileState() != FILEERROR 
          ? SUCCESS 
          : ERROR;
}

//##ModelId=3E2C29B40120
string FileOutputAgent::stateString() const
{
  return fileState() == FILEERROR 
         ? "ERROR " + errorString()
         :  "OK (" + fileStateString() + ")";
}

} // namespace VisAgent
