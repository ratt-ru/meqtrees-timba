#ifndef OCTOGlish_GlishClientWP_h
#define OCTOGlish_GlishClientWP_h 1

#include <aips/Glish.h>
#include <aips/Arrays/Array.h>
#include <aips/Arrays/ArrayMath.h>

#include <DMI/DMI.h>
#include <OCTOGlish/AID-OCTOGlish.h>
#include <OCTOPUSSY/WorkProcess.h>
    
class GlishSysEvent;
class GlishSysEventSource;
class GlishRecord;

#pragma aidgroup OCTOGlish
#pragma aid GlishClientWP
#pragma aid Index start IMTestWP HelloWorld Content


//##ModelId=3CB5618B0373
class GlishClientWP : public WorkProcess
{
  public:
      //##ModelId=3CB562BB0226
      GlishClientWP (GlishSysEventSource *src, bool autostp = True, AtomicID wpc = AidGlishClientWP);

    //##ModelId=3DB9369201C7
      ~GlishClientWP();

      virtual void init ();

      //##ModelId=3CBA97E70232
      virtual bool start ();

      //##ModelId=3CBABEA10165
      virtual void stop ();

      //##ModelId=3CBACB920259
      virtual int input (int , int );

      //##ModelId=3CBACFC6013D
      virtual int timeout (const HIID &);

      //##ModelId=3CB5622B01ED
      virtual int receive (MessageRef &mref);

    // Additional Public Declarations
      // max number of glish events processed per one polling loop
    //##ModelId=3DB93691036B
      static const int MaxEventsPerPoll = 10;
      
  protected:
      GlishValue messageToGlishValue (const Message &msg);
      MessageRef glishValueToMessage (const GlishValue &value);
  
  private:
    //##ModelId=3DB9369503DE
      GlishClientWP();

    //##ModelId=3DB9369600AA
      GlishClientWP(const GlishClientWP &right);

    //##ModelId=3DB9369801DA
      GlishClientWP & operator=(const GlishClientWP &right);

    //##ModelId=3DB9369803A7
      bool autostop () const;

    // Additional Private Declarations
      // shuts down the link
    //##ModelId=3DB9369900E1
      void shutdown ();
      
      
      void handleEvent (GlishSysEvent &event);
      
  private:
    // Data Members for Class Attributes

      //##ModelId=3CB561E2013E
      GlishSysEventSource *evsrc;

      //##ModelId=3CBAE1740040
      bool autostop_;

    // Additional Implementation Declarations
      // flag: have unprocessed events in the stream
    //##ModelId=3DB936920005
      bool connected,glish_started,has_events;
      // tick of oldest unprocessed event
    //##ModelId=3DB936920146
      ulong evtick;
};

// Class GlishClientWP 

//##ModelId=3DB9369803A7
inline bool GlishClientWP::autostop () const
{
  return autostop_;
}

GlishClientWP * makeGlishClientWP (int argv,const char *argv[],bool autstop=False );


#endif
