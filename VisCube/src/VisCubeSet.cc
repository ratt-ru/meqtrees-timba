//##ModelId=3DB964F401F2
    
#include "VisCube/VisCubeSet.h"
#include "VisCubeSet.h"


//##ModelId=3DB964F401F2

// Class VisCubeSet 

VisCubeSet::VisCubeSet()
{
}


//##ModelId=3DB964F401F3
VisCubeSet::VisCubeSet(const VisCubeSet &right,int flags,int depth)
    : BlockableObject()
{
  assign(right,flags,depth);
}


//##ModelId=3DB964F401FB
VisCubeSet::~VisCubeSet()
{
}


//##ModelId=3DB964F401FC
VisCubeSet& VisCubeSet::operator=(const VisCubeSet &right)
{
  assign(right);
  return *this;
}

// instantiate a copyRefContainer template (from DMI/CountedRef.h)
template
void copyRefContainer (deque<VisCube::Ref> &dest,
                       const deque<VisCube::Ref> &src,
                       int flags=DMI::PRESERVE_RW,int depth=-1);

//##ModelId=3DC694770211
void VisCubeSet::assign(const VisCubeSet &other, int flags, int depth)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(other.mutex_);
  cubes.clear();
// Just use regular ref copy, since that insures proper interpretation
// of all flags.
// Note "depth-1" below: if it was 0 to begin with (default), only a copy is done
// If 1, then refs are privatized, etc.
  copyRefContainer(cubes,other.cubes,flags,depth-1);
}

//##ModelId=3DC675980286
void VisCubeSet::setWritable (bool writable)
{
  Thread::Mutex::Lock lock(mutex_);
  if( writable )  // upgrade all cube refs are writable
  {
    for( CI iter = cubes.begin(); iter != cubes.end(); iter++ )
      if( !iter->isWritable() )
        iter->privatize(DMI::WRITE,1); // depth=1 to make cube writable too
  }
  else            // downgrade all refs to readonly
  {
    for( CI iter = cubes.begin(); iter != cubes.end(); iter++ )
      iter->change(DMI::READONLY);
  }
}


//##ModelId=3DD23C430260
void VisCubeSet::push(VisCubeRef ref)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_back(ref);
}

//##ModelId=3DD23CAB01E6
void VisCubeSet::pushFront(VisCubeRef ref)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_front(ref);
}

//##ModelId=3DD23C840029
void VisCubeSet::operator <<=(VisCubeRef ref)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_back(ref);
}

//##ModelId=3DD23C930309
void VisCubeSet::operator <<=(VisCube* cube)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_back(VisCubeRef());
  cubes.back() <<= cube;
}

//##ModelId=3DD23C5A0318
VisCubeRef VisCubeSet::pop()
{
  Thread::Mutex::Lock lock(mutex_);
  VisCubeRef ret = cubes.front();
  cubes.pop_front();
  return ret;
}

//##ModelId=3DD23CCB0339
VisCubeRef VisCubeSet::popBack()
{
  Thread::Mutex::Lock lock(mutex_);
  VisCubeRef ret = cubes.back();
  cubes.pop_back();
  return ret;
}

//##ModelId=3DD23C720071
void VisCubeSet::pop(VisCubeRef &out)
{
  Thread::Mutex::Lock lock(mutex_);
  out = cubes.front();
  cubes.pop_front();
}

//##ModelId=3DD23CDB00C2
void VisCubeSet::popBack(VisCubeRef &out)
{
  Thread::Mutex::Lock lock(mutex_);
  out = cubes.back();
  cubes.pop_back();
}

//##ModelId=3DD4C8A5012B
VisCubeRef VisCubeSet::remove(int icube)
{
  Thread::Mutex::Lock lock(mutex_);
  VisCubeRef ret;
  remove(icube,ret);
  return ret;
}

//##ModelId=3DD4C8AE03D6
void VisCubeSet::remove(int icube, VisCubeRef& out)
{
  Thread::Mutex::Lock lock(mutex_);
  if( icube >= 0 )
  {
    CI iter;
    for( iter = cubes.begin(); icube > 0; icube-- )
      iter++;
    out = *iter;
    cubes.erase(iter);
  }
  else
  {
    RCI iter;
    for( iter = cubes.rbegin(); icube < -1; icube++ )
      iter++;
    out = *iter;
    cubes.erase(iter.base());
  }      
}

//##ModelId=3DC672CA0323
CountedRefTarget* VisCubeSet::clone(int flags, int depth) const
{
  return new VisCubeSet(*this,flags,depth);
}

//##ModelId=3DC672CE034B
void VisCubeSet::privatize(int flags, int depth)
{
  Thread::Mutex::Lock lock(mutex_);
  if( flags&DMI::DEEP || depth>0 )
    for( CI iter = cubes.begin(); iter != cubes.end(); iter++ )
      iter->privatize(flags,depth-1);
}

//##ModelId=3DC672E10339
int VisCubeSet::fromBlock(BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex_);
  int ret = 1;
  cubes.clear();
  // get header block
  FailWhen( set.empty(),"invalid set" );
  set.pop(hdrblock);
  FailWhen( hdrblock->size() != sizeof(HeaderBlock),"invalid block" );
  const HeaderBlock * phdr = hdrblock->const_ptr_cast<HeaderBlock>();
  cubes.resize(phdr->ncubes);
  for( CI iter = cubes.begin(); iter != cubes.end(); iter++ )
  {
    VisCube *pcube = new VisCube;
    (*iter) <<= pcube;
    ret += pcube->fromBlock(set);
  }
  return ret;
}

//##ModelId=3DC672EB001E
int VisCubeSet::toBlock(BlockSet &set) const
{
  Thread::Mutex::Lock lock(mutex_);
  int ret = 1;
  // push out a header block
  if( !hdrblock.valid() )
    hdrblock <<= new SmartBlock(sizeof(HeaderBlock));
  else // else privatize the existing header block
    hdrblock.privatize(DMI::WRITE,0);
  HeaderBlock * phdr = hdrblock().ptr_cast<HeaderBlock>();
  // fill in header
  phdr->ncubes = cubes.size();
  hdrblock.change(DMI::READONLY);
  set.pushCopy(hdrblock);
  
  // convert cubes
  for( CCI iter = cubes.begin(); iter != cubes.end(); iter++ )
    ret += iter->deref().toBlock(set);
  
  return ret;
}



//##ModelId=3DF9FDD20007
string VisCubeSet::sdebug ( int detail,const string &prefix,
                            const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"CI:VisCubeSet",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"size %d",size());
  }
  if( ( detail >= 2 || detail <= -2 ) && size() )
  {
    out += ":";
    for( CCI iter = cubes.begin(); iter != cubes.end(); iter++ )
    {
       out += "\n" + prefix + "    ";
       out += iter->sdebug(detail-1,prefix);
    }
  }
  return out;
}
