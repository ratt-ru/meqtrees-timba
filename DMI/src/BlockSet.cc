#include "BlockSet.h"
    
    
namespace DMI
{
  
//##ModelId=3BFA4B6501A7

BlockSet::BlockSet(const BlockSet &right)
{
  *this = right;
}

//##ModelId=3C3EBCBA0082
BlockSet::BlockSet (int num)
    : refs(num)
{
}

//##ModelId=3DB934480060
BlockSet::BlockSet (BlockSet& right, int flags)
{
  right.copyAll(*this,flags);
}


//##ModelId=3DB93448029B
BlockSet::~BlockSet()
{
}


//##ModelId=3DB9344802F5
BlockSet & BlockSet::operator=(const BlockSet &right)
{
  if( &right != this )
    right.copyAll(*this);
  return *this;
}



//##ModelId=3C3D854D000C
void BlockSet::clear ()
{
  refs.clear();
}

//##ModelId=3BFA537401F6
BlockRef BlockSet::pop ()
{
  FailWhen( refs.empty(),"can't pop from empty set" );
  BlockRef out = refs.front();
  refs.pop_front();
  return out;
}

//##ModelId=3C5AB7F40257
void BlockSet::pop (BlockRef &out)
{
  FailWhen( refs.empty(),"can't pop from empty set" );
  out.xfer(refs.front());
  refs.pop_front();
}

//##ModelId=3BFA56540172
int BlockSet::popMove (BlockSet& outset, int count)
{
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
}

//##ModelId=3BFB873E0091
int BlockSet::push (const BlockRef &ref)
{
  refs.push_back(ref);
  return size();
}

//##ModelId=3C3EB55F00FD
int BlockSet::pushCopy (BlockSet &set, int flags)
{
  int n = size();
  refs.resize( n + set.size() );
  CDQI in_iter = set.refs.begin();
  for( DQI iter = refs.begin()+n; iter != refs.end(); iter++,in_iter++ )
    (*iter).copy(*in_iter,flags);
  return size();
}

//##ModelId=3C5AA4BF0279
int BlockSet::pushCopy (const BlockRef &ref, int flags)
{
  refs.resize( size() + 1 );
  refs.back().copy(ref,flags);
  return size();
}

//##ModelId=3C5AB3880083
BlockRef & BlockSet::pushNew ()
{
  refs.resize( size() + 1 );
  return refs.back();
}

//##ModelId=3BFB89BE02AB
int BlockSet::pushFront (BlockRef ref)
{
  refs.push_front(ref);
  return size();
}

//##ModelId=3BFB85F30334
//##ModelId=3C3EBF410288
int BlockSet::copyAll (BlockSet &out, int flags) const
{
  int n = out.size();
  out.refs.resize( n + size() );
  DQI oiter = out.refs.begin()+n;
//  out.refs.reserve(size());
  for( CDQI iter = refs.begin(); iter != refs.end(); iter++,oiter++ )
    (*oiter).copy(*iter,flags);
  return out.size();
}

//##ModelId=3BFB8A3301D6
int BlockSet::privatizeAll (int flags)
{
  for( DQI iter = refs.begin(); iter != refs.end(); iter++ )
    (*iter).privatize(flags);
  return size();
}

//##ModelId=3BFB8E980315
size_t BlockSet::initCursor ()
{
  size_t total = 0;
  for( CDQI iter = refs.begin(); iter != refs.end(); iter++ )
    total += (*iter)->size();
  cursor_iter = refs.begin();
  cursor_offset = 0;
  return total;
}

//##ModelId=3BFB8EDC0019
const void * BlockSet::getCursorData (size_t  &size)
{
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
    size = std::min(size,remains);
    cursor_offset += size;
    return data;
  }
  return 0; // end of data
}

//##ModelId=3BFB8F5E01E3
int BlockSet::flushToCursor ()
{
  // if cursor points past end of ref, advance it until it hits a valid ref
  while( cursor_iter != refs.end() && cursor_offset >= cursorSize() )
  {
    cursor_iter++;
    cursor_offset = 0;
  }
  // erase all refs up to (excluding) the cursor
  refs.erase(refs.begin(),cursor_iter);
  return size();
}

// Additional Declarations
//##ModelId=3DB9344A009F
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

};
