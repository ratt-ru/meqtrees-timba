//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F3000C3.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F3000C3.cm

//## begin module%3C7B7F3000C3.cp preserve=no
//## end module%3C7B7F3000C3.cp

//## Module: WorkProcess%3C7B7F3000C3; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\WorkProcess.h

#ifndef WorkProcess_h
#define WorkProcess_h 1

//## begin module%3C7B7F3000C3.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C7B7F3000C3.additionalIncludes

//## begin module%3C7B7F3000C3.includes preserve=yes
//## end module%3C7B7F3000C3.includes

// WPInterface
#include "OCTOPUSSY/WPInterface.h"
// Dispatcher
#include "OCTOPUSSY/Dispatcher.h"
//## begin module%3C7B7F3000C3.declarations preserve=no
//## end module%3C7B7F3000C3.declarations

//## begin module%3C7B7F3000C3.additionalDeclarations preserve=yes
#pragma aid /MsgLog /LogNormal /LogWarning /LogError /LogFatal /LogDebug
//## end module%3C7B7F3000C3.additionalDeclarations


//## begin WorkProcess%3C8F25430087.preface preserve=yes
//## end WorkProcess%3C8F25430087.preface

//## Class: WorkProcess%3C8F25430087; Abstract
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C8F3679014E;Dispatcher { -> }

class WorkProcess : public WPInterface  //## Inherits: <unnamed>%3C8F263A00E6
{
  //## begin WorkProcess%3C8F25430087.initialDeclarations preserve=yes
  //## end WorkProcess%3C8F25430087.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: WorkProcess%3C8F25DB014E
      WorkProcess (AtomicID wpc);


    //## Other Operations (specified)
      //## Operation: addTimeout%3C7D285803B0
      void addTimeout (const Timestamp &period, const HIID &id = HIID(), int flags = 0, int priority = Message::PRI_EVENT);

      //## Operation: addInput%3C7D2874023E
      void addInput (int fd, int flags, int priority = Message::PRI_EVENT);

      //## Operation: addSignal%3C7DFE520239
      void addSignal (int signum, int flags = 0, int priority = Message::PRI_EVENT);

      //## Operation: removeTimeout%3C7D287F02C6
      bool removeTimeout (const HIID &id);

      //## Operation: removeInput%3C7D28A30141
      bool removeInput (int fd, int flags = EV_FDALL);

      //## Operation: removeSignal%3C7DFE480253
      bool removeSignal (int signum);

      //## Operation: detachMyself%3C95A89D015E
      void detachMyself ();

      //## Operation: attachWP%3C95BA1602D9
      const MsgAddress & attachWP (WPRef &wpref);

      //## Operation: attachWP%3C95BA1A02D5
      const MsgAddress & attachWP (WPInterface* wp, int flags);

    // Additional Public Declarations
      //## begin WorkProcess%3C8F25430087.public preserve=yes
      //## end WorkProcess%3C8F25430087.public

  protected:
    // Additional Protected Declarations
      //## begin WorkProcess%3C8F25430087.protected preserve=yes
      //## end WorkProcess%3C8F25430087.protected

  private:
    //## Constructors (generated)
      WorkProcess();

      WorkProcess(const WorkProcess &right);

    //## Assignment Operation (generated)
      WorkProcess & operator=(const WorkProcess &right);

    // Additional Private Declarations
      //## begin WorkProcess%3C8F25430087.private preserve=yes
      //## end WorkProcess%3C8F25430087.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin WorkProcess%3C8F25430087.implementation preserve=yes
      //## end WorkProcess%3C8F25430087.implementation

};

//## begin WorkProcess%3C8F25430087.postscript preserve=yes
//## end WorkProcess%3C8F25430087.postscript

// Class WorkProcess 

//## begin module%3C7B7F3000C3.epilog preserve=yes
//## end module%3C7B7F3000C3.epilog


#endif
