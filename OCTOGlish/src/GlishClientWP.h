#ifndef GlishClientWP_h
#define GlishClientWP_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include "OCTOGlish/AID-OCTOGlish.h"

// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
#pragma aidgroup OCTOGlish
#pragma aid GlishClientWP
#pragma aid start IMTestWP HelloWorld Content

class GlishSysEvent;
class GlishSysEventSource;
class GlishRecord;


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

      //##ModelId=3CB57C8401D6
      MessageRef glishRecToMessage (const GlishRecord &glrec);

      //##ModelId=3CB57CA00280
      bool messageToGlishRec (const Message &msg, GlishRecord &glrec);

    // Additional Public Declarations
      // max number of glish events processed per one polling loop
    //##ModelId=3DB93691036B
      static const int MaxEventsPerPoll = 10;
      
    //##ModelId=3DB9369202CC
      static void recToGlish (const DataRecord &rec, GlishRecord& glrec);
    //##ModelId=3DB936930231
      static void objectToBlockRec (const BlockableObject &obj,GlishRecord &rec );
      
  protected:
    // Additional Protected Declarations
    //##ModelId=3DB936940034
      void glishToRec (const GlishRecord &glrec, DataRecord& rec);
    //##ModelId=3DB93695024D
      BlockableObject * blockRecToObject (const GlishRecord &rec );
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

GlishClientWP * makeGlishClientWP (int argv,const char *argv[] );


#endif
