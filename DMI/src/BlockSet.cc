#include "BlockSet.h"
    
    
namespace DMI
{
  
//##ModelId=3BFA56540172
int BlockSet::popMove (BlockSet& outset, int count)
{
  FailWhen( count>size(),"Too many refs requested in popMove" );
  for( int i=0; i<count; i++ )
  {
    outset.pushNew().xfer(refs.front());
    refs.pop_front();
  }
  return cursize -= count;
}


//##ModelId=3C3EB55F00FD
int BlockSet::pushCopy (const BlockSet &set, int flags)
{
  BlockList::const_iterator iter = set.refs.begin();
  for( ; iter != set.refs.end(); iter++ )
  {
    refs.push_back(BlockRef());
    refs.back().copy(*iter,flags);
  }
  return cursize += set.size();
}

//##ModelId=3BFB8A3301D6
int BlockSet::privatizeAll (int flags)
{
  for( BlockList::iterator iter = refs.begin(); iter != refs.end(); iter++ )
    (*iter).privatize(flags);
  return size();
}

//##ModelId=3BFB8E980315
size_t BlockSet::initCursor ()
{
  size_t total = 0;
  for( BlockList::const_iterator iter = refs.begin(); iter != refs.end(); iter++ )
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
    for( BlockList::const_iterator iter = refs.begin(); iter != refs.end(); iter++ )
      Debug::append(out,(*iter).sdebug(0,"",""));
    out += " }";
  }
  // higher detail - append ref list at higher detail
  if( ( detail >= 2 || detail <= -2 ) && size() )
  {
    for( BlockList::const_iterator iter = refs.begin(); iter != refs.end(); iter++ )
    {
      if( out.length() )
        out += "\n"+prefix;
      out += "    "+(*iter).sdebug(abs(detail)-1,prefix+"    ","");
    }
  }
  return out;
}

};
