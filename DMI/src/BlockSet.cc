//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC81023B.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC81023B.cm

//## begin module%3C10CC81023B.cp preserve=no
//## end module%3C10CC81023B.cp

//## Module: BlockSet%3C10CC81023B; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\BlockSet.cc

//## begin module%3C10CC81023B.additionalIncludes preserve=no
//## end module%3C10CC81023B.additionalIncludes

//## begin module%3C10CC81023B.includes preserve=yes
//## end module%3C10CC81023B.includes

// BlockSet
#include "DMI/BlockSet.h"
//## begin module%3C10CC81023B.declarations preserve=no
//## end module%3C10CC81023B.declarations

//## begin module%3C10CC81023B.additionalDeclarations preserve=yes
//## end module%3C10CC81023B.additionalDeclarations


// Class BlockSet 

BlockSet::BlockSet(const BlockSet &right)
  //## begin BlockSet::BlockSet%3BEA80A703A9_copy.hasinit preserve=no
  //## end BlockSet::BlockSet%3BEA80A703A9_copy.hasinit
  //## begin BlockSet::BlockSet%3BEA80A703A9_copy.initialization preserve=yes
  //## end BlockSet::BlockSet%3BEA80A703A9_copy.initialization
{
  //## begin BlockSet::BlockSet%3BEA80A703A9_copy.body preserve=yes
  *this = right;
  //## end BlockSet::BlockSet%3BEA80A703A9_copy.body
}

BlockSet::BlockSet (int num)
  //## begin BlockSet::BlockSet%3BFA4B6501A7.hasinit preserve=no
  //## end BlockSet::BlockSet%3BFA4B6501A7.hasinit
  //## begin BlockSet::BlockSet%3BFA4B6501A7.initialization preserve=yes
    : refs(num)
  //## end BlockSet::BlockSet%3BFA4B6501A7.initialization
{
  //## begin BlockSet::BlockSet%3BFA4B6501A7.body preserve=yes
  //## end BlockSet::BlockSet%3BFA4B6501A7.body
}

BlockSet::BlockSet (BlockSet& right, int flags)
  //## begin BlockSet::BlockSet%3C3EBCBA0082.hasinit preserve=no
  //## end BlockSet::BlockSet%3C3EBCBA0082.hasinit
  //## begin BlockSet::BlockSet%3C3EBCBA0082.initialization preserve=yes
  //## end BlockSet::BlockSet%3C3EBCBA0082.initialization
{
  //## begin BlockSet::BlockSet%3C3EBCBA0082.body preserve=yes
  right.copyAll(*this,flags);
  //## end BlockSet::BlockSet%3C3EBCBA0082.body
}


BlockSet::~BlockSet()
{
  //## begin BlockSet::~BlockSet%3BEA80A703A9_dest.body preserve=yes
  //## end BlockSet::~BlockSet%3BEA80A703A9_dest.body
}


BlockSet & BlockSet::operator=(const BlockSet &right)
{
  //## begin BlockSet::operator=%3BEA80A703A9_assign.body preserve=yes
  if( &right != this )
    right.copyAll(*this);
  return *this;
  //## end BlockSet::operator=%3BEA80A703A9_assign.body
}



//## Other Operations (implementation)
void BlockSet::clear ()
{
  //## begin BlockSet::clear%3C3D854D000C.body preserve=yes
  refs.resize(0);
  //## end BlockSet::clear%3C3D854D000C.body
}

BlockRef BlockSet::pop ()
{
  //## begin BlockSet::pop%3BFA537401F6.body preserve=yes
  BlockRef out = refs.front();
  refs.pop_front();
  return out;
  //## end BlockSet::pop%3BFA537401F6.body
}

void BlockSet::pop (BlockRef &out)
{
  //## begin BlockSet::pop%3C5AB7F40257.body preserve=yes
  out.xfer(refs.front());
  refs.pop_front();
  //## end BlockSet::pop%3C5AB7F40257.body
}

int BlockSet::popMove (BlockSet& outset, int count)
{
  //## begin BlockSet::popMove%3BFA56540172.body preserve=yes
  FailWhen( count>size(),"Too many refs requested in popMove" );
  int n = outset.size();
  outset.refs.resize( n + count );
//  out.refs.reserve(size());
  for( DQI oiter = outset.refs.begin()+n; count>0; oiter++,count-- )
  {
    (*oiter).xfer(refs.front());
    refs.pop_front();
  }
  return size();
  //## end BlockSet::popMove%3BFA56540172.body
}

int BlockSet::push (const BlockRef &ref)
{
  //## begin BlockSet::push%3BFB873E0091.body preserve=yes
  refs.push_back(ref);
  return size();
  //## end BlockSet::push%3BFB873E0091.body
}

int BlockSet::pushCopy (BlockSet &set, int flags)
{
  //## begin BlockSet::pushCopy%3C3EB55F00FD.body preserve=yes
  int n = size();
  refs.resize( n + set.size() );
  CDQI in_iter = set.refs.begin();
  for( DQI iter = refs.begin()+n; iter != refs.end(); iter++,in_iter++ )
    (*iter).copy(*in_iter,flags);
  return size();
  //## end BlockSet::pushCopy%3C3EB55F00FD.body
}

int BlockSet::pushCopy (const BlockRef &ref, int flags)
{
  //## begin BlockSet::pushCopy%3C5AA4BF0279.body preserve=yes
  refs.resize( size() + 1 );
  refs.back().copy(ref,flags);
  return size();
  //## end BlockSet::pushCopy%3C5AA4BF0279.body
}

BlockRef & BlockSet::pushNew ()
{
  //## begin BlockSet::pushNew%3C5AB3880083.body preserve=yes
  refs.resize( size() + 1 );
  return refs.back();
  //## end BlockSet::pushNew%3C5AB3880083.body
}

int BlockSet::pushFront (BlockRef ref)
{
  //## begin BlockSet::pushFront%3BFB89BE02AB.body preserve=yes
  refs.push_front(ref);
  return size();
  //## end BlockSet::pushFront%3BFB89BE02AB.body
}

int BlockSet::copyAll (BlockSet &out, int flags) const
{
  //## begin BlockSet::copyAll%3BFB85F30334.body preserve=yes
  // disallow the MAKE_READONLY flag...
  FailWhen(flags&DMI::MAKE_READONLY,"const violation for MAKE_READONLY");
  // ...and defer to non-const version in all other respects
  return ((BlockSet*)this)->copyAll(out,flags);
  //## end BlockSet::copyAll%3BFB85F30334.body
}

int BlockSet::copyAll (BlockSet &out, int flags)
{
  //## begin BlockSet::copyAll%3C3EBF410288.body preserve=yes
  int n = out.size();
  out.refs.resize( n + size() );
  DQI oiter = out.refs.begin()+n;
//  out.refs.reserve(size());
  for( DQI iter = refs.begin(); iter != refs.end(); iter++,oiter++ )
  {
    (*oiter).copy(*iter,flags);
    if( flags&DMI::MAKE_READONLY )
      (*iter).change(DMI::READONLY);
  }
  return out.size();
  //## end BlockSet::copyAll%3C3EBF410288.body
}

int BlockSet::privatizeAll (int flags)
{
  //## begin BlockSet::privatizeAll%3BFB8A3301D6.body preserve=yes
  for( DQI iter = refs.begin(); iter != refs.end(); iter++ )
    (*iter).privatize(flags);
  return size();
  //## end BlockSet::privatizeAll%3BFB8A3301D6.body
}

size_t BlockSet::initCursor ()
{
  //## begin BlockSet::initCursor%3BFB8E980315.body preserve=yes
  size_t total = 0;
  for( CDQI iter = refs.begin(); iter != refs.end(); iter++ )
    total += (*iter)->size();
  cursor_iter = refs.begin();
  cursor_offset = 0;
  return total;
  //## end BlockSet::initCursor%3BFB8E980315.body
}

const void * BlockSet::getCursorData (size_t  &size)
{
  //## begin BlockSet::getCursorData%3BFB8EDC0019.body preserve=yes
  while( cursor_iter != refs.end() ) 
  {
    // how much data left in current ref?
    size_t remains = cursorSize() - cursor_offset;
    if( !remains ) 
    {  // none - goto next ref
      cursor_iter++;
      cursor_offset = 0;
      continue;
    }
    // get and return chunk of data
    const void *data = cursor_offset + (char*)(*cursor_iter)->data();
    size = min(size,remains);
    cursor_offset += size;
    return data;
  }
  return 0; // end of data
  //## end BlockSet::getCursorData%3BFB8EDC0019.body
}

int BlockSet::flushToCursor ()
{
  //## begin BlockSet::flushToCursor%3BFB8F5E01E3.body preserve=yes
  // if cursor points past end of ref, advance it until it hits a valid ref
  while( cursor_iter != refs.end() && cursor_offset >= cursorSize() )
  {
    cursor_iter++;
    cursor_offset = 0;
  }
  // erase all refs up to (excluding) the cursor
  refs.erase(refs.begin(),cursor_iter);
  return size();
  //## end BlockSet::flushToCursor%3BFB8F5E01E3.body
}

// Additional Declarations
  //## begin BlockSet%3BEA80A703A9.declarations preserve=yes
string BlockSet::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  if( detail >= 0 )
    Debug::appendf(out,"%s@%8p #:%d",name?name:"BlockSet",this,size());
  // normal detail -- add short ref list
  if( ( detail == 1 || detail == -1 ) && size() )
  {
    if( out.length() )
      out += "\n"+prefix+"  {";
    for( CDQI iter = refs.begin(); iter != refs.end(); iter++ )
      Debug::append(out,(*iter).sdebug(0,"",""));
    out += " }";
  }
  // higher detail - append ref list at higher detail
  if( ( detail >= 2 || detail <= -2 ) && size() )
  {
    for( CDQI iter = refs.begin(); iter != refs.end(); iter++ )
    {
      if( out.length() )
        out += "\n"+prefix;
      out += "    "+(*iter).sdebug(abs(detail)-1,prefix+"    ","");
    }
  }
  return out;
}
  //## end BlockSet%3BEA80A703A9.declarations
//## begin module%3C10CC81023B.epilog preserve=yes
//## end module%3C10CC81023B.epilog
