#ifndef OCTOGLISH_GlishConnServerWP_h
#define OCTOGLISH_GlishConnServerWP_h 1

#include <DMI/Common.h>
#include <DMI/DMI.h>

#include <OCTOPUSSY/WorkProcess.h>
#pragma aid GlishConnServerWP

namespace casa {
class GlishSysEventSource;
}

    
class GlishConnServerWP : public WorkProcess
{
  public:
      GlishConnServerWP (std::string path = "");

      ~GlishConnServerWP();


      virtual void init ();

      virtual bool start ();

      virtual void stop ();

      virtual int input (int , int );
      
      LocalDebugContext;

  private:
      GlishConnServerWP(const GlishConnServerWP &right);

      GlishConnServerWP & operator=(const GlishConnServerWP &right);

      // helper function creates a Glish event source
      static casa::GlishSysEventSource * makeEventSource (std::vector<std::string> &args);

      // path to pipe for receiving new commnections
      std::string connpath_;
      // fd of open pipe
      int connfd_;
      // flag: true if we created the pipe (will delete on exit)
      bool created_;
      
      
      char readbuf_[1024];
      size_t bufpos_;
};

// Class GlishConnServerWP 


#endif
