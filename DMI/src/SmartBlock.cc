//##ModelId=3BEBD44D0103
//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC83016E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC83016E.cm

//## begin module%3C10CC83016E.cp preserve=no
//## end module%3C10CC83016E.cp

//## Module: SmartBlock%3C10CC83016E; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\SmartBlock.cc

//## begin module%3C10CC83016E.additionalIncludes preserve=no
//## end module%3C10CC83016E.additionalIncludes

//## begin module%3C10CC83016E.includes preserve=yes
//## end module%3C10CC83016E.includes

// SmartBlock
#include "DMI/SmartBlock.h"
//## begin module%3C10CC83016E.declarations preserve=no
//## end module%3C10CC83016E.declarations

//## begin module%3C10CC83016E.additionalDeclarations preserve=yes
//## end module%3C10CC83016E.additionalDeclarations


// Class SmartBlock 

SmartBlock::SmartBlock()
  //## begin SmartBlock::SmartBlock%3BEAACAB0041_const.hasinit preserve=no
  //## end SmartBlock::SmartBlock%3BEAACAB0041_const.hasinit
  //## begin SmartBlock::SmartBlock%3BEAACAB0041_const.initialization preserve=yes
  : block(0),datasize(0),shmid(0)
  //## end SmartBlock::SmartBlock%3BEAACAB0041_const.initialization
{
  //## begin SmartBlock::SmartBlock%3BEAACAB0041_const.body preserve=yes
  dprintf(2)("default constructor\n");
  //## end SmartBlock::SmartBlock%3BEAACAB0041_const.body
}

//##ModelId=3BFE299902D7
SmartBlock::SmartBlock (void* data, size_t size, int flags)
  //## begin SmartBlock::SmartBlock%3BEBD44D0103.hasinit preserve=no
  //## end SmartBlock::SmartBlock%3BEBD44D0103.hasinit
  //## begin SmartBlock::SmartBlock%3BEBD44D0103.initialization preserve=yes
  : block(0),datasize(0),shmid(0)
  //## end SmartBlock::SmartBlock%3BEBD44D0103.initialization
{
  //## begin SmartBlock::SmartBlock%3BEBD44D0103.body preserve=yes
  dprintf(2)("constructor(data=%x,size=%d,fl=%x)\n",(int)data,size,flags);
  init(data,size,flags,0);
  //## end SmartBlock::SmartBlock%3BEBD44D0103.body
}

//##ModelId=3BFA4FCA0387
SmartBlock::SmartBlock (size_t size, int flags)
  //## begin SmartBlock::SmartBlock%3BFE299902D7.hasinit preserve=no
  //## end SmartBlock::SmartBlock%3BFE299902D7.hasinit
  //## begin SmartBlock::SmartBlock%3BFE299902D7.initialization preserve=yes
  : block(0),datasize(0),shmid(0)
  //## end SmartBlock::SmartBlock%3BFE299902D7.initialization
{
  //## begin SmartBlock::SmartBlock%3BFE299902D7.body preserve=yes
  dprintf(2)("constructor(size=%d,fl=%x)\n",size,flags);
  init( new char[size],size,flags|DMI::DELETE,0 );
  //## end SmartBlock::SmartBlock%3BFE299902D7.body
}

//##ModelId=3BFE303F0022
SmartBlock::SmartBlock (size_t size, int shm_flags, int flags)
  //## begin SmartBlock::SmartBlock%3BFA4FCA0387.hasinit preserve=no
  //## end SmartBlock::SmartBlock%3BFA4FCA0387.hasinit
  //## begin SmartBlock::SmartBlock%3BFA4FCA0387.initialization preserve=yes
  : block(0),datasize(0),shmid(0)
  //## end SmartBlock::SmartBlock%3BFA4FCA0387.initialization
{
  //## begin SmartBlock::SmartBlock%3BFA4FCA0387.body preserve=yes
  dprintf(2)("constructor(size=%d,shmfl=%x,fl=%x)",size,shm_flags,flags);
  init(0,size,flags|DMI::SHMEM,shm_flags);
  //## end SmartBlock::SmartBlock%3BFA4FCA0387.body
}

//##ModelId=3DB934E50248
SmartBlock::SmartBlock (const SmartBlock &other, int flags)
  //## begin SmartBlock::SmartBlock%3BFE303F0022.hasinit preserve=no
  //## end SmartBlock::SmartBlock%3BFE303F0022.hasinit
  //## begin SmartBlock::SmartBlock%3BFE303F0022.initialization preserve=yes
  : CountedRefTarget(),block(0),datasize(0),shmid(0)
  //## end SmartBlock::SmartBlock%3BFE303F0022.initialization
{
  //## begin SmartBlock::SmartBlock%3BFE303F0022.body preserve=yes
  dprintf(2)("copy constructor(%s,%x)\n",other.debug(),flags);
  FailWhen( !(flags&DMI::CLONE),"must use DMI::CLONE to copy")
  *this = other;
  //## end SmartBlock::SmartBlock%3BFE303F0022.body
}


//##ModelId=3DB934E6004B
SmartBlock::~SmartBlock()
{
  //## begin SmartBlock::~SmartBlock%3BEAACAB0041_dest.body preserve=yes
  dprintf1(2)("%s: destructor\n",debug());
  destroy();
  //## end SmartBlock::~SmartBlock%3BEAACAB0041_dest.body
}


//##ModelId=3DB934E802CD
SmartBlock & SmartBlock::operator=(const SmartBlock &right)
{
  //## begin SmartBlock::operator=%3BEAACAB0041_assign.body preserve=yes
  if( &right != this )
  {
    dprintf(2)("assignment of %s\n",right.debug());
    destroy();
    // clone the block
    if( !right.size() )
      return *this;
    block = new char[ datasize = right.size() ];
    delete_block = True;
    memcpy(block,*right,datasize);
  }
  return *this;
  //## end SmartBlock::operator=%3BEAACAB0041_assign.body
}



//##ModelId=3BFE37C3022B
//## Other Operations (implementation)
void SmartBlock::init (void* data, size_t size, int flags, int shm_flags)
{
  //## begin SmartBlock::init%3BFE37C3022B.body preserve=yes
  if( block || datasize || shmid )
    destroy();
  FailWhen(size && !data,"attempt to init() null block");
  FailWhen( flags&DMI::SHMEM,"shared memory not yet implemented" );
  block = static_cast<char*>(data);
  datasize = size;
  delete_block = (flags&DMI::DELETE)!=0;
  shmid = 0;
  if( flags&DMI::ZERO )
    memset(block,0,datasize);
  dprintf1(2)("%s allocated\n",debug());
  //## end SmartBlock::init%3BFE37C3022B.body
}

//##ModelId=3C639C340295
void SmartBlock::resize (size_t newsize, int flags)
{
  //## begin SmartBlock::resize%3C639C340295.body preserve=yes
  // if resizing an empty block, just init
  if( !block || !datasize )
  {
    if( newsize )
      init( new char[newsize],newsize,flags|DMI::DELETE,0 );
  }
  else
  {
  // allocate new block and copy data
    char *newblock = 0;
    if( newsize )
    {
      newblock = new char[newsize];
      memcpy(newblock,block,min(datasize,newsize));
    // pad with 0 if needed
      if( newsize > datasize && flags&DMI::ZERO )
        memset(newblock+datasize,0,newsize-datasize);
    // get rid of old block
    }
    destroy();
    init( newblock,newsize,flags|DMI::DELETE,0 );
  }
  //## end SmartBlock::resize%3C639C340295.body
}

//##ModelId=3C1E0D8D0391
void SmartBlock::destroy ()
{
  //## begin SmartBlock::destroy%3C1E0D8D0391.body preserve=yes
  dprintf(2)("%s: destroying\n",debug());
  if( block && delete_block )
    delete [] static_cast<char*>(block); 
  block=0; datasize=0; shmid=0;
  //## end SmartBlock::destroy%3C1E0D8D0391.body
}

//##ModelId=3BFE23B501F4
CountedRefTarget * SmartBlock::clone (int flags, int depth) const
{
  //## begin SmartBlock::clone%3BFE23B501F4.body preserve=yes
  dprintf1(2)("%s: cloning\n",debug());
  return new SmartBlock(*this,flags|DMI::CLONE);
  //## end SmartBlock::clone%3BFE23B501F4.body
}

// Additional Declarations
//##ModelId=3DB934E7024B
  //## begin SmartBlock%3BEAACAB0041.declarations preserve=yes
string SmartBlock::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  if( detail >= 0 )
    Debug::appendf(out,"%s/%08x",name?name:"SmartBlk",(int)this);
  // normal detail 
  if( detail >= 1 || detail == -1 )
  {
    if( size()>10000 )
      Debug::appendf(out,"%c%08x:%dK",delete_block?'D':'-',(int)data(),size()/1024);
    else
      Debug::appendf(out,"%c%08x:%db",delete_block?'D':'-',(int)data(),size());
    if( isShMem() )
      Debug::appendf(out,"shmid:%x",getShmid());
    Debug::append(out,CountedRefTarget::sdebug(-1));
  }
  // high detail - tack on info from base class (ref list)
  if( detail >= 2 || detail == -2 )   
  {
    Debug::append(out,CountedRefTarget::sdebug(-abs(detail),prefix),"\n  "+prefix);
  }
  return out;
}
  //## end SmartBlock%3BEAACAB0041.declarations
//## begin module%3C10CC83016E.epilog preserve=yes
//## end module%3C10CC83016E.epilog
