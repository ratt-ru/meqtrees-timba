//  CountedRefTarget.cc: abstract prototype for a ref target
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include <DMI/CountedRefBase.h>
#include <DMI/CountedRefTarget.h>

namespace DMI
{
  
#define DebugContext (CountedRefBase::getDebugContext())

#ifdef USE_THREADS
  #define threadLock Thread::Mutex::Lock t##_lock(cref_mutex_)
#else
  #define threadLock 
#endif

//##ModelId=3DB93466002B
CountedRefTarget::CountedRefTarget()
  : anon_(false)
{
#ifdef COUNTEDREF_LINKED_LIST
  owner_ref_ = 0;
#else
  ref_count_ = 0;
#endif

}

//##ModelId=3DB934660053
CountedRefTarget::CountedRefTarget(const CountedRefTarget &)
  : anon_(false)
{
#ifdef COUNTEDREF_LINKED_LIST
  owner_ref_ = 0;
#else
  ref_count_ = 0;
#endif
}

//##ModelId=3DB9346600F3
CountedRefTarget::~CountedRefTarget()
{
  threadLock;
#ifdef COUNTEDREF_LINKED_LIST
  if( owner_ref_ )
  {
    dprintf(2)("%s destructor:\n  %s\n",debug(),debug(-2,"  "));
    // anon object can only be deleted by releasing its refs
    FailWhen( anon_,"can't delete anon object: refs attached");
    // check for locked refs
    for( const CountedRefBase *ref = owner_ref_; ref!=0; ref = ref->getNext() )
      FailWhen( ref->isLocked(),"can't delete object: locked refs attached" );
    // if OK, then invalidate all refs
    CountedRefBase *ref = owner_ref_;
    while( ref )
    {
      CountedRefBase *nextref = ref->getNext();
      dprintf(3)("%s: invalidating %s\n",debug(0),ref->debug());
      ref->empty();
      ref = nextref;
    }
  }
#else
  FailWhen(anon_ && ref_count_,"can't delete anon object: refs attached");
#endif
}

#ifdef COUNTEDREF_LINKED_LIST
//##ModelId=3C18899002BB
int CountedRefTarget::targetReferenceCount () const
{
  int count = 0;
  threadLock;
  for( const CountedRefBase *ref = getTargetOwner(); ref != 0; ref = ref->getNext() )
    count++;
  return count;
}
#endif

//##ModelId=3E01BE070204
void CountedRefTarget::print () const
{ 
  print(std::cout); 
  std::cout<<endl;
}
 
//##ModelId=3DB9346602E8
string CountedRefTarget::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  threadLock;
  if( detail >= 0 )
    Debug::appendf(out,"%s/%p",name?name:"CRefTarg",(const void*)this);
  // normal detail 
  if( detail >= 1 || detail == -1 )
  {
    Debug::appendf(out,"rc:%d",targetReferenceCount()); 
  }
#ifdef COUNTEDREF_LINKED_LIST
  // high detail - append ref list
  if( detail >= 2 || detail <= -2 )   
  {
    for( const CountedRefBase *ref = getTargetOwner(); ref != 0; ref = ref->getNext() )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += "<-R"+ref->sdebug(1,prefix+"    ","");
    }
  }
#endif
  return out;
}

}; // namespace DMI
