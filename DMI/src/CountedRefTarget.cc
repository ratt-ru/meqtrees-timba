//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8103D8.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8103D8.cm

//## begin module%3C10CC8103D8.cp preserve=no
//## end module%3C10CC8103D8.cp

//## Module: CountedRefTarget%3C10CC8103D8; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\cep\cpa\pscf\src\CountedRefTarget.cc

//## begin module%3C10CC8103D8.additionalIncludes preserve=no
//## end module%3C10CC8103D8.additionalIncludes

//## begin module%3C10CC8103D8.includes preserve=yes
//## end module%3C10CC8103D8.includes

// CountedRefBase
#include "DMI/CountedRefBase.h"
// CountedRefTarget
#include "DMI/CountedRefTarget.h"
//## begin module%3C10CC8103D8.declarations preserve=no
//## end module%3C10CC8103D8.declarations

//## begin module%3C10CC8103D8.additionalDeclarations preserve=yes
#define DebugContext (CountedRefBase::getDebugContext())
//## end module%3C10CC8103D8.additionalDeclarations


// Class SingularRefTarget 

// Additional Declarations
  //## begin SingularRefTarget%3C8CDBB901EB.declarations preserve=yes
  //## end SingularRefTarget%3C8CDBB901EB.declarations

// Class CountedRefTarget 

CountedRefTarget::CountedRefTarget()
  //## begin CountedRefTarget::CountedRefTarget%3C0CDF41029F_const.hasinit preserve=no
  //## end CountedRefTarget::CountedRefTarget%3C0CDF41029F_const.hasinit
  //## begin CountedRefTarget::CountedRefTarget%3C0CDF41029F_const.initialization preserve=yes
  : owner_ref(0)
  //## end CountedRefTarget::CountedRefTarget%3C0CDF41029F_const.initialization
{
  //## begin CountedRefTarget::CountedRefTarget%3C0CDF41029F_const.body preserve=yes
  //## end CountedRefTarget::CountedRefTarget%3C0CDF41029F_const.body
}

CountedRefTarget::CountedRefTarget(const CountedRefTarget &right)
  //## begin CountedRefTarget::CountedRefTarget%3C0CDF41029F_copy.hasinit preserve=no
  //## end CountedRefTarget::CountedRefTarget%3C0CDF41029F_copy.hasinit
  //## begin CountedRefTarget::CountedRefTarget%3C0CDF41029F_copy.initialization preserve=yes
  : owner_ref(0)
  //## end CountedRefTarget::CountedRefTarget%3C0CDF41029F_copy.initialization
{
  //## begin CountedRefTarget::CountedRefTarget%3C0CDF41029F_copy.body preserve=yes
  //## end CountedRefTarget::CountedRefTarget%3C0CDF41029F_copy.body
}


CountedRefTarget::~CountedRefTarget()
{
  //## begin CountedRefTarget::~CountedRefTarget%3C0CDF41029F_dest.body preserve=yes
  if( owner_ref )
  {
    dprintf(2)("%s destructor:\n  %s\n",debug(),debug(-2,"  "));
    // anon object can only be deleted by releasing its refs
    FailWhen( owner_ref->isAnonObject(),
        "can't delete anon object: refs attached");
    // check for locked refs
    for( const CountedRefBase *ref = owner_ref; ref!=0; ref = ref->getNext() )
      FailWhen( ref->isLocked(),"can't delete object: locked refs attached" );
    // if OK, then invalidate all refs
    CountedRefBase *ref = owner_ref;
    while( ref )
    {
      CountedRefBase *nextref = ref->getNext();
      dprintf(3)("%s: invalidating %s\n",debug(0),ref->debug());
      ref->empty();
      ref = nextref;
    }
  }
  //## end CountedRefTarget::~CountedRefTarget%3C0CDF41029F_dest.body
}



//## Other Operations (implementation)
void CountedRefTarget::privatize (int flags, int depth)
{
  //## begin CountedRefTarget::privatize%3C3EDD7D0301.body preserve=yes
  //## end CountedRefTarget::privatize%3C3EDD7D0301.body
}

int CountedRefTarget::refCount () const
{
  //## begin CountedRefTarget::refCount%3C18899002BB.body preserve=yes
  int count = 0;
  for( const CountedRefBase *ref = getOwner(); ref != 0; ref = ref->getNext() )
    count++;
  return count;
  //## end CountedRefTarget::refCount%3C18899002BB.body
}

int CountedRefTarget::refCountWrite () const
{
  //## begin CountedRefTarget::refCountWrite%3C18C69A0120.body preserve=yes
  int count = 0;
  for( const CountedRefBase *ref = getOwner(); ref != 0; ref = ref->getNext() )
    if( ref->isWritable() )
      count++;
  return count;
  //## end CountedRefTarget::refCountWrite%3C18C69A0120.body
}

bool CountedRefTarget::refWriteExclusions () const
{
  //## begin CountedRefTarget::refWriteExclusions%3C18C6A603DA.body preserve=yes
  for( const CountedRefBase *ref = getOwner(); ref != 0; ref = ref->getNext() )
    if( ref->isExclusiveWrite() )
      return True;
  return False;
  //## end CountedRefTarget::refWriteExclusions%3C18C6A603DA.body
}

bool CountedRefTarget::hasExternalRefs () const
{
  //## begin CountedRefTarget::hasExternalRefs%3C63B97601B9.body preserve=yes
  return owner_ref && !owner_ref->isAnonObject();
  //## end CountedRefTarget::hasExternalRefs%3C63B97601B9.body
}

bool CountedRefTarget::hasAnonRefs () const
{
  //## begin CountedRefTarget::hasAnonRefs%3C63BA8800B9.body preserve=yes
  return owner_ref && owner_ref->isAnonObject();
  //## end CountedRefTarget::hasAnonRefs%3C63BA8800B9.body
}

// Additional Declarations
  //## begin CountedRefTarget%3C0CDF41029F.declarations preserve=yes
string CountedRefTarget::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  if( detail >= 0 )
    Debug::appendf(out,"%s/%08x",name?name:"CRefTarg",(int)this);
  // normal detail 
  if( detail >= 1 || detail == -1 )
  {
    Debug::appendf(out,"R:%d WR:%d%s",
        refCount(),refCountWrite(),refWriteExclusions()?"/X":""); 
  }
  // high detail - append ref list
  if( detail >= 2 || detail <= -2 )   
  {
    for( const CountedRefBase *ref = getOwner(); ref != 0; ref = ref->getNext() )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += "<-R"+ref->sdebug(1,prefix+"    ","");
    }
  }
  return out;
}
  //## end CountedRefTarget%3C0CDF41029F.declarations
//## begin module%3C10CC8103D8.epilog preserve=yes
//## end module%3C10CC8103D8.epilog
