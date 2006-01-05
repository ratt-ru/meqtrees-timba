#ifndef _VISAGENT_VISAGENTVOCABULARY_H
#define _VISAGENT_VISAGENTVOCABULARY_H

#include <AppAgent/FileChannel.h>    
#include <AppAgent/AID-AppAgent.h>
#include <VisCube/VisVocabulary.h>
    
#pragma aidgroup AppAgent
#pragma aid Vis Input Output Agent Parameters 
#pragma aid Data Header Footer Tile Suspend Resume
    
namespace AppAgent
{    
    
namespace VisData
{
  using VisVocabulary::FVDSID;
  
  const AtomicID VisEventPrefix = AidVis;
  
  // these are used as event types below, and also as channel state
  const int HEADER  = -AidHeader_int;
  const int DATA    = -AidData_int;
  const int FOOTER  = -AidFooter_int;
  
  const HIID  _VisEventMask = VisEventPrefix|AidWildcard;

  inline const HIID & VisEventMask () 
  { return _VisEventMask; }
  
  inline HIID VisEventHIID (int type,const HIID &instance)
  { return VisEventPrefix|AtomicID(-type)|instance; }
  
  inline HIID VisEventMask (int type)
  { return VisEventHIID(type,AidWildcard); }
  
  inline int VisEventType  (const HIID &event)
  { return -( event[1].id() ); }
  
  inline HIID VisEventInstance (const HIID &event)
  { return event.subId(2); }
  
  const HIID 
       // suspend/resume events
       SuspendEvent    = AidVis|AidSuspend,
       ResumeEvent     = AidVis|AidResume;
      
  inline string codeToString (int code)
  { return AtomicID(-code).toString(); }
};

};    
#endif
