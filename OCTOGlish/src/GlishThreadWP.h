#ifndef OCTOGlish_GlishThreadClientWP_h
#define OCTOGlish_GlishThreadClientWP_h 1

#include <OCTOGlish/GlishClientWP.h>
    
#pragma aidgroup OCTOGlish
#pragma aid GlishThreadedClientWP

class GlishThreadedClientWP : public GlishClientWP
{
  public:
      // note that we use two glish event sources (two agents) here:
      // src is passed on to GlishClientWP, and used to _SEND_ events
      // to Glish, while spigot is maintained in the receiveThread here,
      // and used to _RECEIVE_ events
      GlishThreadedClientWP (casa::GlishSysEventSource *src,
			     casa::GlishSysEventSource *spig,
                             bool autostp=True,AtomicID wpc=AidGlishClientWP);

      ~GlishThreadedClientWP();

      virtual void init ();

      virtual bool start ();

      virtual void stop ();

  protected:
      static void * start_receiveThread (void *pwp);
      
      void * receiveThread ();
      
      casa::GlishSysEventSource & eventSpigot ()
      { return *evspigot; }

  private:
      GlishThreadedClientWP();
      GlishThreadedClientWP(const GlishClientWP &right);
      GlishThreadedClientWP & operator=(const GlishClientWP &right);

      casa::GlishSysEventSource *evspigot;
      
      Thread::ThrID rcv_thread_;
};

#endif
