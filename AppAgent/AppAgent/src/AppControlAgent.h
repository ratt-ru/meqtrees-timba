#ifndef APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
#define APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
#include <AppAgent/AppAgent.h>
#include <AppAgent/AID-AppAgent.h>

#pragma aid App Stop Init Reinit Event Terminate
namespace AppControlAgentVocabulary
{
  const HIID 
      InitEvent       = AidApp|AidInit|AidEvent,
      StopEvent       = AidApp|AidStop|AidEvent,
      ReinitEvent     = AidApp|AidReinit|AidEvent,
      PauseEvent      = AidApp|AidPause|AidEvent,
      ResumeEvent     = AidApp|AidResume|AidEvent,
      TerminateEvent  = AidApp|AidTerminate|AidEvent,
      
      __last_declaration = 0;
};
    
//##ModelId=3DFF2FC1009C
class AppControlAgent : public AppAgent
{
  public:
    //##ModelId=3DFF35700297
    static const HIID & InitEvent ()      { return AppControlAgentVocabulary::InitEvent; }
    //##ModelId=3DFF357002AB
    static const HIID & StopEvent ()      { return AppControlAgentVocabulary::StopEvent; }
    //##ModelId=3DFF357002BE
    static const HIID & ReinitEvent ()    { return AppControlAgentVocabulary::ReinitEvent; }
    //##ModelId=3DFF357002D2
    static const HIID & TerminateEvent () { return AppControlAgentVocabulary::TerminateEvent; }
      
};



#endif /* APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733 */
