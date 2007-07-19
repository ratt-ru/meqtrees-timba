//##ModelId=3BEBD44D0103
//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "SmartBlock.h"

namespace DMI
{

SmartBlock::SmartBlock()
  : block(0),datasize(0),shmid(0),delete_block(false)
{
  dprintf(2)("default constructor\n");
}

//##ModelId=3BFE299902D7
SmartBlock::SmartBlock (void* data, size_t size, int flags)
  : block(0),datasize(0),shmid(0),delete_block(false)
{
  dprintf(2)("constructor(data=%p,size=%d,fl=%x)\n",data,size,flags);
  init(data,size,flags,0);
}

//##ModelId=3BFA4FCA0387
SmartBlock::SmartBlock (size_t size, int flags)
  : block(0),datasize(0),shmid(0),delete_block(false)
{
  dprintf(2)("constructor(size=%d,fl=%x)\n",size,flags);
  init( new char[size],size,flags|DMI::ANON,0 );
}

//##ModelId=3BFE303F0022
SmartBlock::SmartBlock (size_t size, int shm_flags, int flags)
  : block(0),datasize(0),shmid(0),delete_block(false)
{
  dprintf(2)("constructor(size=%d,shmfl=%x,fl=%x)",size,shm_flags,flags);
  init(0,size,flags|DMI::SHMEM,shm_flags);
}

//##ModelId=3DB934E50248
SmartBlock::SmartBlock (const SmartBlock &other, int flags)
  : CountedRefTarget(),block(0),datasize(0),shmid(0),delete_block(false)
{
  dprintf(2)("copy constructor(%s,%x)\n",other.debug(),flags);
  FailWhen( !(flags&DMI::CLONE),"must use DMI::CLONE to copy");
  *this = other;
}


//##ModelId=3DB934E6004B
SmartBlock::~SmartBlock()
{
  dprintf1(2)("%s: destructor\n",debug());
  destroy();
}


//##ModelId=3DB934E802CD
SmartBlock & SmartBlock::operator=(const SmartBlock &right)
{
  if( &right != this )
  {
    dprintf(2)("assignment of %s\n",right.debug());
    destroy();
    // clone the block
    if( !right.size() )
      return *this;
    block = new char[ datasize = right.size() ];
    delete_block = true;
    memcpy(block,*right,datasize);
  }
  return *this;
}



//##ModelId=3BFE37C3022B
void SmartBlock::init (void* data, size_t size, int flags, int /*shm_flags*/)
{
  if( block || datasize || shmid )
    destroy();
  FailWhen(size && !data,"attempt to init() null block");
  FailWhen( flags&DMI::SHMEM,"shared memory not yet implemented" );
  block = static_cast<char*>(data);
  datasize = size;
  delete_block = (flags&DMI::ANON)!=0;
  shmid = 0;
  if( flags&DMI::ZERO )
    memset(block,0,datasize);
  dprintf1(2)("%s allocated\n",debug());
}

//##ModelId=3C639C340295
void SmartBlock::resize (size_t newsize, int flags)
{
  // if resizing an empty block, just init
  if( !block || !datasize )
  {
    if( newsize )
      init( new char[newsize],newsize,flags|DMI::ANON,0 );
  }
  else
  {
  // allocate new block and copy data
    char *newblock = 0;
    if( newsize )
    {
      newblock = new char[newsize];
      memcpy(newblock,block,std::min(datasize,newsize));
    // pad with 0 if needed
      if( newsize > datasize && flags&DMI::ZERO )
        memset(newblock+datasize,0,newsize-datasize);
    // get rid of old block
    }
    destroy();
    init( newblock,newsize,flags|DMI::ANON,0 );
  }
}

//##ModelId=3C1E0D8D0391
void SmartBlock::destroy ()
{
  dprintf(2)("%s: destroying\n",debug());
  if( block && delete_block )
    delete [] static_cast<char*>(block); 
  block=0; datasize=0; shmid=0;
}

//##ModelId=3BFE23B501F4
CountedRefTarget * SmartBlock::clone (int flags, int) const
{
  dprintf1(2)("%s: cloning\n",debug());
  return new SmartBlock(*this,flags|DMI::CLONE);
}

// Additional Declarations
//##ModelId=3DB934E7024B
string SmartBlock::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  if( detail>=0 ) // basic detail
  {
    out = name ? name : "SmartBlock";
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += Debug::ssprintf("/%p",(void*)this);
    if( size()>10000 )
      Debug::appendf(out,"%c%p:%dK",delete_block?'D':'-',data(),size()/1024);
    else
      Debug::appendf(out,"%c%p:%db",delete_block?'D':'-',data(),size());
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



};
