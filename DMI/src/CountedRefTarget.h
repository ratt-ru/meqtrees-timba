//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8103D6.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8103D6.cm

//## begin module%3C10CC8103D6.cp preserve=no
//## end module%3C10CC8103D6.cp

//## Module: CountedRefTarget%3C10CC8103D6; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\CountedRefTarget.h

#ifndef CountedRefTarget_h
#define CountedRefTarget_h 1

//## begin module%3C10CC8103D6.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC8103D6.additionalIncludes

//## begin module%3C10CC8103D6.includes preserve=yes
//## end module%3C10CC8103D6.includes


class CountedRefBase;

//## begin module%3C10CC8103D6.declarations preserve=no
//## end module%3C10CC8103D6.declarations

//## begin module%3C10CC8103D6.additionalDeclarations preserve=yes
//## end module%3C10CC8103D6.additionalDeclarations


//## begin CountedRefTarget%3C0CDF41029F.preface preserve=yes
//## end CountedRefTarget%3C0CDF41029F.preface

//## Class: CountedRefTarget%3C0CDF41029F; Abstract
//	Abstract base class for anything that can be referenced by a Counted
//	Ref.
//## Category: PSCF::DMI%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class CountedRefTarget 
{
  //## begin CountedRefTarget%3C0CDF41029F.initialDeclarations preserve=yes
  //## end CountedRefTarget%3C0CDF41029F.initialDeclarations

  public:
    //## Constructors (generated)
      CountedRefTarget();

      CountedRefTarget(const CountedRefTarget &right);

    //## Destructor (generated)
      virtual ~CountedRefTarget();


    //## Other Operations (specified)
      //## Operation: clone%3C0CE728002B; C++
      //	Abstract method for cloning an object. Should return pointer to new
      //	object. Flags: DMI::WRITE if writable clone is required, DMI::DEEP
      //	for deep cloning (i.e. contents of object will be cloned as well).
      virtual CountedRefTarget* clone (int flags = 0) const = 0;

      //## Operation: privatize%3C3EDD7D0301
      //	Virtual method for privatization of an object. If the object
      //	contains other refs, they should be privatized by this method. The
      //	DMI::DEEP flag should be passed on to child refs, for deep
      //	privatization.
      virtual void privatize (int flags = 0);

      //## Operation: refCount%3C18899002BB; C++
      //	Returns a reference count. Note that the ref count methods may be
      //	redefined in derived classes (i.e. SmartBlock) to support, e.g.,
      //	shared memory (i.e. refs from multiple processes), in which case
      //	they are only compelled to be accurate to 0, 1 or 2 ("more").
      virtual int refCount () const;

      //## Operation: refCountWrite%3C18C69A0120; C++
      //	Returns a count of writable refs.
      virtual int refCountWrite () const;

      //## Operation: refWriteExclusions%3C18C6A603DA; C++
      //	Returns True is exclusive-write refs to the object exist.
      virtual bool refWriteExclusions () const;

    //## Get and Set Operations for Associations (generated)

      //## Association: PSCF::DMI::<unnamed>%3C0CDF6500AC
      //## Role: CountedRefTarget::owner_ref%3C0CDF6503B9
      //	First ref in list of refs to this target
      const CountedRefBase * getOwner () const;

    // Additional Public Declarations
      //## begin CountedRefTarget%3C0CDF41029F.public preserve=yes
      CountedRefBase * getOwner ();
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug().
      virtual string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
      
      //## end CountedRefTarget%3C0CDF41029F.public
  protected:
    // Additional Protected Declarations
      //## begin CountedRefTarget%3C0CDF41029F.protected preserve=yes
      //## end CountedRefTarget%3C0CDF41029F.protected

  private:
    // Data Members for Associations

      //## Association: PSCF::DMI::<unnamed>%3C0CDF6500AC
      //## begin CountedRefTarget::owner_ref%3C0CDF6503B9.role preserve=no  public: CountedRefBase {0..1 -> 0..1RFHNM}
      mutable CountedRefBase *owner_ref;
      //## end CountedRefTarget::owner_ref%3C0CDF6503B9.role

    // Additional Private Declarations
      //## begin CountedRefTarget%3C0CDF41029F.private preserve=yes
      //## end CountedRefTarget%3C0CDF41029F.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin CountedRefTarget%3C0CDF41029F.implementation preserve=yes
      //## end CountedRefTarget%3C0CDF41029F.implementation

  //## begin CountedRefTarget%3C0CDF41029F.friends preserve=no
    friend class CountedRefBase;
  //## end CountedRefTarget%3C0CDF41029F.friends
};

//## begin CountedRefTarget%3C0CDF41029F.postscript preserve=yes
//## end CountedRefTarget%3C0CDF41029F.postscript

// Class CountedRefTarget 

//## Get and Set Operations for Associations (inline)

inline const CountedRefBase * CountedRefTarget::getOwner () const
{
  //## begin CountedRefTarget::getOwner%3C0CDF6503B9.get preserve=no
  return owner_ref;
  //## end CountedRefTarget::getOwner%3C0CDF6503B9.get
}

//## begin module%3C10CC8103D6.epilog preserve=yes
inline CountedRefBase * CountedRefTarget::getOwner () 
{
  return owner_ref;
}
//## end module%3C10CC8103D6.epilog


#endif
