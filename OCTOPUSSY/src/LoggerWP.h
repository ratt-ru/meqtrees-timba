//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CA04546008E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CA04546008E.cm

//## begin module%3CA04546008E.cp preserve=no
//## end module%3CA04546008E.cp

//## Module: LoggerWP%3CA04546008E; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\LoggerWP.h

#ifndef LoggerWP_h
#define LoggerWP_h 1

//## begin module%3CA04546008E.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3CA04546008E.additionalIncludes

//## begin module%3CA04546008E.includes preserve=yes
#include <stdio.h>
//## end module%3CA04546008E.includes

// WorkProcess
#include "OCTOPUSSY/WorkProcess.h"
//## begin module%3CA04546008E.declarations preserve=no
//## end module%3CA04546008E.declarations

//## begin module%3CA04546008E.additionalDeclarations preserve=yes
#pragma aid LoggerWP
//## end module%3CA04546008E.additionalDeclarations


//## begin LoggerWP%3CA044DE02AB.preface preserve=yes
//## end LoggerWP%3CA044DE02AB.preface

//## Class: LoggerWP%3CA044DE02AB
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class LoggerWP : public WorkProcess  //## Inherits: <unnamed>%3CA044E9021B
{
  //## begin LoggerWP%3CA044DE02AB.initialDeclarations preserve=yes
  //## end LoggerWP%3CA044DE02AB.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: LoggerWP%3CA0451401B9
      LoggerWP (int maxlev = 9999, int scope = Message::GLOBAL);

    //## Destructor (generated)
      ~LoggerWP();


    //## Other Operations (specified)
      //## Operation: init%3CA045020054
      virtual void init ();

      //## Operation: stop%3CA05A7E01CE
      virtual void stop ();

      //## Operation: receive%3CA0450C0103
      virtual int receive (MessageRef &mref);

      //## Operation: setScope%3CA04AF50212
      void setScope (int scope);

      //## Operation: logMessage%3CA04A1F03D7
      virtual void logMessage (const string &source, const string &msg, int level, AtomicID type);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: level%3CA048E90395
      int level () const;
      void setLevel (int value);

      //## Attribute: consoleLevel%3CA052560312
      int consoleLevel () const;
      void setConsoleLevel (int value);

    // Additional Public Declarations
      //## begin LoggerWP%3CA044DE02AB.public preserve=yes
      //## end LoggerWP%3CA044DE02AB.public

  protected:
    // Additional Protected Declarations
      //## begin LoggerWP%3CA044DE02AB.protected preserve=yes
      //## end LoggerWP%3CA044DE02AB.protected

  private:
    //## Constructors (generated)
      LoggerWP(const LoggerWP &right);

    //## Assignment Operation (generated)
      LoggerWP & operator=(const LoggerWP &right);

    // Additional Private Declarations
      //## begin LoggerWP%3CA044DE02AB.private preserve=yes
      //## end LoggerWP%3CA044DE02AB.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin LoggerWP::level%3CA048E90395.attr preserve=no  public: int {U} 
      int level_;
      //## end LoggerWP::level%3CA048E90395.attr

      //## begin LoggerWP::consoleLevel%3CA052560312.attr preserve=no  public: int {U} 
      int consoleLevel_;
      //## end LoggerWP::consoleLevel%3CA052560312.attr

    // Additional Implementation Declarations
      //## begin LoggerWP%3CA044DE02AB.implementation preserve=yes
      int scope_;
      
      string filename_;
      int fd;
      //## end LoggerWP%3CA044DE02AB.implementation
};

//## begin LoggerWP%3CA044DE02AB.postscript preserve=yes
//## end LoggerWP%3CA044DE02AB.postscript

// Class LoggerWP 

//## Get and Set Operations for Class Attributes (inline)

inline int LoggerWP::level () const
{
  //## begin LoggerWP::level%3CA048E90395.get preserve=no
  return level_;
  //## end LoggerWP::level%3CA048E90395.get
}

inline void LoggerWP::setLevel (int value)
{
  //## begin LoggerWP::setLevel%3CA048E90395.set preserve=no
  level_ = value;
  //## end LoggerWP::setLevel%3CA048E90395.set
}

inline int LoggerWP::consoleLevel () const
{
  //## begin LoggerWP::consoleLevel%3CA052560312.get preserve=no
  return consoleLevel_;
  //## end LoggerWP::consoleLevel%3CA052560312.get
}

inline void LoggerWP::setConsoleLevel (int value)
{
  //## begin LoggerWP::setConsoleLevel%3CA052560312.set preserve=no
  consoleLevel_ = value;
  //## end LoggerWP::setConsoleLevel%3CA052560312.set
}

//## begin module%3CA04546008E.epilog preserve=yes
//## end module%3CA04546008E.epilog


#endif
