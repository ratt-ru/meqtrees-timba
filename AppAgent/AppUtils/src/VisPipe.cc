#include "VisPipe.h"

namespace AppAgent
{    
    
//##ModelId=3E7728010327
VisPipe::VisPipe()
    : ApplicationBase(),input_(0),output_(0)
{
}

//##ModelId=3E7725FA03DE
void VisPipe::attach(VisAgent::InputAgent *inp, int flags)
{
  AppAgent::Ref ref(inp,flags|DMI::WRITE|DMI::SHARED);
  FailWhen(input_,"input agent already attached");
  input_ = inp;
  attachRef(ref);
}

//##ModelId=3E7725FB0002
void VisPipe::attach(VisAgent::OutputAgent *outp, int flags)
{
  AppAgent::Ref ref(outp,flags|DMI::WRITE|DMI::SHARED);
  FailWhen(output_,"output agent already attached");
  output_ = outp;
  attachRef(ref);
}

//##ModelId=3E78955E0197
bool VisPipe::verifySetup (bool throw_exc) const
{
  if( !ApplicationBase::verifySetup(throw_exc) )
    return false;
  if( throw_exc )
  {
    FailWhen(!hasInputAgent(),"input agent not attached");
    FailWhen(!hasOutputAgent(),"output agent not attached");
    return true;
  }
  else
    return hasInputAgent() && hasOutputAgent();
}

};
