#include "AppEventAgentBase.h"

//##ModelId=3E414887001F
AppEventAgentBase::AppEventAgentBase (const HIID &initf)
    : AppAgent(initf)
{
  sink_ <<= new AppEventSink(HIID());
}

//##ModelId=3E4148870295
AppEventAgentBase::AppEventAgentBase (AppEventSink &evsink, const HIID &initf)
    : AppAgent(initf)
{
  sink_.attach(evsink,DMI::WRITE); // attach default ref (extern if first ref)
}

//##ModelId=3E41147B0049
bool AppEventAgentBase::init (const DataRecord &data)
{
  return sink().init(data);
}

//##ModelId=3E41147E0126
void AppEventAgentBase::close ()
{
  sink().close();
}

//##ModelId=3E41141201DE
int AppEventAgentBase::state () const
{
  return sink().state();
}

//##ModelId=3E411412024B
string AppEventAgentBase::stateString () const
{
  return sink().stateString();
}

//##ModelId=3E4148900162
string AppEventAgentBase::sdebug (int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"AppEventAgentBase",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"st:%d",state());
  }
  if( detail >= 2 || detail == -2 )
  {
    append(out,stateString());
  }
  if( detail >= 3 || detail == -3 )
  {
    out += "\n" + prefix + "  sink: " + sink().sdebug(abs(detail)-1,prefix+"  ");
  }
  
  return out;
}
