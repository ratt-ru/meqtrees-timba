#ifndef LoggerWP_h
#define LoggerWP_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include <stdio.h>

// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
#pragma aid LoggerWP


//##ModelId=3CA044DE02AB
class LoggerWP : public WorkProcess
{
  public:
      //##ModelId=3CA0451401B9
      LoggerWP (int maxlev = 9999, int scope = Message::GLOBAL);

    //##ModelId=3DB9369A0073
      ~LoggerWP();


      //##ModelId=3CA045020054
      virtual void init ();

      //##ModelId=3CA05A7E01CE
      virtual void stop ();

      //##ModelId=3CA0450C0103
      virtual int receive (MessageRef &mref);

      //##ModelId=3CA04AF50212
      void setScope (int scope);

      //##ModelId=3CA04A1F03D7
      virtual void logMessage (const string &source, const string &msg, int level, AtomicID type);

    //##ModelId=3DB9369A018C
      int level () const;
    //##ModelId=3DB9369A01F0
      void setLevel (int value);

    //##ModelId=3DB9369A02B8
      int consoleLevel () const;
    //##ModelId=3DB9369A0330
      void setConsoleLevel (int value);

  private:
    //##ModelId=3DB9369B0043
      LoggerWP(const LoggerWP &right);

    //##ModelId=3DB9369B016F
      LoggerWP & operator=(const LoggerWP &right);

  private:
    // Data Members for Class Attributes

      //##ModelId=3CA048E90395
      int level_;

      //##ModelId=3CA052560312
      int consoleLevel_;

    // Additional Implementation Declarations
    //##ModelId=3DB9369902DF
      int scope_;
      
    //##ModelId=3DB936990361
      string filename_;
    //##ModelId=3DB9369903CF
      int fd;
};

// Class LoggerWP 

//##ModelId=3DB9369A018C
inline int LoggerWP::level () const
{
  return level_;
}

//##ModelId=3DB9369A01F0
inline void LoggerWP::setLevel (int value)
{
  level_ = value;
}

//##ModelId=3DB9369A02B8
inline int LoggerWP::consoleLevel () const
{
  return consoleLevel_;
}

//##ModelId=3DB9369A0330
inline void LoggerWP::setConsoleLevel (int value)
{
  consoleLevel_ = value;
}


#endif
