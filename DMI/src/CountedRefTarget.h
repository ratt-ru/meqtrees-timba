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
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\CountedRefTarget.h

#ifndef CountedRefTarget_h
#define CountedRefTarget_h 1

//## begin module%3C10CC8103D6.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
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
//## Category: DOMIN0%3BEAB1F2006B; Global
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
      //	Abstract method for cloning an object. Should allocate a new object
      //	with "new" and return pointer to it. If DMI::WRITE is specified,
      //	then a writable clone is required.
      //	The depth argument specifies cloning depth (the DMI::DEEP flag
      //	means infinite depth). If depth=0, then any nested refs should only
      //	be copy()d. ). If depth>0, then nested refs should be copied and
      //	privatize()d , with depth=depth-1.
      //	The DMI::DEEP flag  corresponds to infinitely deep cloning. If this
      //	is set, then depth should be ignored, and nested refs should be
      //	privatize()d with DMI::DEEP.
      //
      //	 Otherwise, nested refs should be copied & privatized  with
      //	depth=depth-1 and the DMI::DEEP flag passed on.
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const = 0;

      //## Operation: privatize%3C3EDD7D0301
      //	Virtual method for privatization of an object.
      //	The depth argument determines the depth of privatization and/or
      //	cloning (see CountedRefBase::privatize()). If depth>0, then any
      //	nested refs should be privatize()d as well, with depth=depth-1.
      //	The DMI::DEEP flag  corresponds to infinitely deep privatization. If
      //	this is set, then depth should be ignored, and nested refs should be
      //	privatize()d with DMI::DEEP.
      //	If depth=0 (and DMI::DEEP is not set), then privatize() is
      //	effectively a no-op. However, if your class has a 'writable'
      //	property, it should be changed in accordance with the DMI::WRITE
      //	and/or DMI::READONLY flags.
      virtual void privatize (int flags = 0, int depth = 0);

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

      //## Operation: hasExternalRefs%3C63B97601B9
      bool hasExternalRefs () const;

      //## Operation: hasAnonRefs%3C63BA8800B9
      bool hasAnonRefs () const;

    //## Get and Set Operations for Associations (generated)

      //## Association: DOMIN0::<unnamed>%3C0CDF6500AC
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

      //## Association: DOMIN0::<unnamed>%3C0CDF6500AC
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

//## begin SingularRefTarget%3C8CDBB901EB.preface preserve=yes
//## end SingularRefTarget%3C8CDBB901EB.preface

//## Class: SingularRefTarget%3C8CDBB901EB; Abstract
//	SingularRefTarget is simply a CountedRefTarget with clone()
//	redefined to throw an exception (hence the name 'singular', since
//	such a target cannot be cloned). You can derive your classes from
//	SingularRefTarget if you just want to make use of CountedRefs as
//	auto pointers (i.e., to automatically delete an object once the last
//	ref has been detached), but do not want to implement cloning or
//	privatization.
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class SingularRefTarget : public CountedRefTarget  //## Inherits: <unnamed>%3C8CDBE1013E
{
  //## begin SingularRefTarget%3C8CDBB901EB.initialDeclarations preserve=yes
  //## end SingularRefTarget%3C8CDBB901EB.initialDeclarations

  public:

    //## Other Operations (specified)
      //## Operation: clone%3C8CDBF40236; C++
      //	Abstract method for cloning an object. Should allocate a new object
      //	with "new" and return pointer to it. If DMI::WRITE is specified,
      //	then a writable clone is required.
      //	The depth argument specifies cloning depth (the DMI::DEEP flag
      //	means infinite depth). If depth=0, then any nested refs should only
      //	be copy()d. ). If depth>0, then nested refs should be copied and
      //	privatize()d , with depth=depth-1.
      //	The DMI::DEEP flag  corresponds to infinitely deep cloning. If this
      //	is set, then depth should be ignored, and nested refs should be
      //	privatize()d with DMI::DEEP.
      //
      //	 Otherwise, nested refs should be copied & privatized  with
      //	depth=depth-1 and the DMI::DEEP flag passed on.
      virtual CountedRefTarget* clone (int  = 0, int  = 0) const;

    // Additional Public Declarations
      //## begin SingularRefTarget%3C8CDBB901EB.public preserve=yes
      //## end SingularRefTarget%3C8CDBB901EB.public

  protected:
    // Additional Protected Declarations
      //## begin SingularRefTarget%3C8CDBB901EB.protected preserve=yes
      //## end SingularRefTarget%3C8CDBB901EB.protected

  private:
    // Additional Private Declarations
      //## begin SingularRefTarget%3C8CDBB901EB.private preserve=yes
      //## end SingularRefTarget%3C8CDBB901EB.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin SingularRefTarget%3C8CDBB901EB.implementation preserve=yes
      //## end SingularRefTarget%3C8CDBB901EB.implementation

};

//## begin SingularRefTarget%3C8CDBB901EB.postscript preserve=yes
//## end SingularRefTarget%3C8CDBB901EB.postscript

// Class CountedRefTarget 

//## Get and Set Operations for Associations (inline)

inline const CountedRefBase * CountedRefTarget::getOwner () const
{
  //## begin CountedRefTarget::getOwner%3C0CDF6503B9.get preserve=no
  return owner_ref;
  //## end CountedRefTarget::getOwner%3C0CDF6503B9.get
}

// Class SingularRefTarget 


//## Other Operations (inline)
inline CountedRefTarget* SingularRefTarget::clone (int , int ) const
{
  //## begin SingularRefTarget::clone%3C8CDBF40236.body preserve=yes
  Throw("can't clone a singular target");
  //## end SingularRefTarget::clone%3C8CDBF40236.body
}

//## begin module%3C10CC8103D6.epilog preserve=yes
inline CountedRefBase * CountedRefTarget::getOwner () 
{
  return owner_ref;
}
//## end module%3C10CC8103D6.epilog


#endif
