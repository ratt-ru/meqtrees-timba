#ifndef APPUTILS_VISREPEATER_H_HEADER_INCLUDED_BB5EBE76
#define APPUTILS_VISREPEATER_H_HEADER_INCLUDED_BB5EBE76
    
#include <AppAgent/AppControlAgent.h>
#include <VisAgent/InputAgent.h>
#include <VisAgent/OutputAgent.h>
#include <Common/Thread.h>
#include <Common/Thread/Mutex.h>
#include <AppUtils/AID-AppUtils.h>
#include <AppUtils/ApplicationBase.h>

#pragma aidgroup AppUtils
#pragma aid Repeater Input Output Seq Error Closed
    
namespace VisRepeaterVocabulary
{
  const HIID
      InputClosedEvent  = AidInput|AidClosed,
      InputErrorEvent   = AidInput|AidError,
      OutputErrorEvent  = AidOutput|AidError,
      OutputSequenceEvent  = AidOutput|AidSeq|AidError;
  
  // define additional control states
  typedef enum 
  {
      OUTPUT_ERROR  = 1024,     // error on output stream, still running
      INPUT_CLOSED  = -1024,    // input stream has been closed
      INPUT_ERROR   = -1025     // error on input stream
          
  } AppStates;
    
};
        
//##ModelId=3E39285A0273
class VisRepeater : public ApplicationBase
{
  public:
    //##ModelId=3E392BA5005C
    VisRepeater (VisAgent::InputAgent& in, VisAgent::OutputAgent& out, AppControlAgent& ctrl);
  
    //##ModelId=3E392C570286
    virtual void run (DataRecord::Ref &initrec);
    
    //##ModelId=3E392EDF034C
    virtual int state() const;
    //##ModelId=3E392EE403C8
    virtual string stateString() const;
    
    //##ModelId=3E3FEB5002A5
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3E3FEDB80357
    LocalDebugSubContext;
    
  private:
    //##ModelId=3E392B780351
    VisRepeater();
    //##ModelId=3E392B78035E
    VisRepeater(const VisRepeater& right);
    //##ModelId=3E392B78038F
    VisRepeater& operator=(const VisRepeater& right);
    
    //##ModelId=3E43939D03D0
    VisAgent::InputAgent & input;
    //##ModelId=3E43939E0001
    VisAgent::OutputAgent & output;
    //##ModelId=3E43939E001B
    AppControlAgent & control;
};

#endif /* DATAREPEATER_H_HEADER_INCLUDED_BB5EBE76 */
