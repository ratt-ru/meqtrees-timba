#ifndef APPAGENT_SRC_APPEVENTAGENTBASE_H_HEADER_INCLUDED_D87E2C76
#define APPAGENT_SRC_APPEVENTAGENTBASE_H_HEADER_INCLUDED_D87E2C76
    
#include <AppAgent/AppAgent.h>
#include <AppAgent/AppEventSink.h>
    
//##ModelId=3E4147EF00D6
class AppEventAgentBase : public AppAgent
{
  public:
    //##ModelId=3E4150BC00F9
    typedef enum
    {
      // import some symbols from AppEventSink
      SUCCESS   = AppEventSink::SUCCESS,
      WAIT      = AppEventSink::WAIT,     // no event pending, must wait
      OUTOFSEQ  = AppEventSink::OUTOFSEQ, // request is out of sequence (see below)
      CLOSED    = AppEventSink::CLOSED,   // event stream is closed or disconnected
      ERROR     = AppEventSink::ERROR,    // generic error code
          
      NOWAIT    = AppEventSink::NOWAIT, 
      BLOCK     = AppEventSink::BLOCK,  
          
    } ReturnCodes;
    
    //##ModelId=3E41147B0049
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DataRecord.
    virtual bool init(const DataRecord &data);

    //##ModelId=3E41147E0126
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
    virtual void close();

    //##ModelId=3E41141201DE
    //##Documentation
    //## Returns agent state
    virtual int state() const;

    //##ModelId=3E411412024B
    //##Documentation
    //## Returns agent state as a string
    virtual string stateString() const;

    //##ModelId=3E4148900162
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;


  protected:
    //##ModelId=3E414887001F
    explicit AppEventAgentBase(const HIID &initf);

    //##ModelId=3E4148870295
    AppEventAgentBase(AppEventSink &sink, const HIID &initf);
    
    //##ModelId=3E414A8301CB
    AppEventSink & sink();
    
    //##ModelId=3E414AC00074
    const AppEventSink & sink() const;
    
  private:
    //##ModelId=3E41495203E0
    AppEventAgentBase (const AppEventAgentBase& right);

    //##ModelId=3E41495303B7
    AppEventAgentBase& operator= (const AppEventAgentBase& right);
    //##ModelId=3E414C0A00D4
    AppEventAgentBase();
    
    //##ModelId=3E424AAC0172
    AppEventSink::Ref sink_;

};

//##ModelId=3E414A8301CB
inline AppEventSink & AppEventAgentBase::sink()
{
  return sink_.dewr();
}

//##ModelId=3E414AC00074
inline const AppEventSink & AppEventAgentBase::sink() const
{
  return sink_.deref();
}

#endif /* VISAGENT_SRC_VISAGENTBASE_H_HEADER_INCLUDED_D87E2C76 */
