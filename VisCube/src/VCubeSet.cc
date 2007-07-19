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

#include "VCubeSet.h"

namespace VisCube 
{

VCubeSet::VCubeSet()
{
}


//##ModelId=3DB964F401F3
VCubeSet::VCubeSet(const VCubeSet &right,int flags,int depth)
    : DMI::BObj()
{
  assign(right,flags,depth);
}


//##ModelId=3DB964F401FB
VCubeSet::~VCubeSet()
{
}


//##ModelId=3DB964F401FC
VCubeSet& VCubeSet::operator=(const VCubeSet &right)
{
  assign(right);
  return *this;
}

}
namespace DMI
{
// instantiate a copyRefContainer template (from DMI/CountedRef.h)
template
void copyRefContainer (std::deque<VisCube::VCube::Ref> &dest,
                       const std::deque<VisCube::VCube::Ref> &src,
                       int flags=0,int depth=0);
}
namespace VisCube
{

//##ModelId=3DC694770211
void VCubeSet::assign(const VCubeSet &other, int flags, int depth)
{
  Thread::Mutex::Lock lock(mutex_);
  Thread::Mutex::Lock lock2(other.mutex_);
  cubes.clear();
// Just use regular ref copy, since that insures proper interpretation
// of all flags.
// Note "depth-1" below: if it was 0 to begin with (default), only a copy is done
// If 1, then refs are privatized, etc.
  DMI::copyRefContainer(cubes,other.cubes,flags,depth-1);
}

//##ModelId=3DD23C430260
void VCubeSet::push(const VCube::Ref &ref)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_back(ref);
}

//##ModelId=3DD23CAB01E6
void VCubeSet::pushFront(const VCube::Ref &ref)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_front(ref);
}

//##ModelId=3DD23C840029
void VCubeSet::operator <<= (VCube::Ref &ref)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_back(VCube::Ref());
  cubes.back().xfer(ref);
} 

//##ModelId=3DD23C930309
void VCubeSet::operator <<= (VCube* cube)
{
  Thread::Mutex::Lock lock(mutex_);
  cubes.push_back(VCube::Ref());
  cubes.back() <<= cube;
}

//##ModelId=3DD23C5A0318
VCube::Ref VCubeSet::pop()
{
  Thread::Mutex::Lock lock(mutex_);
  VCube::Ref ret;
  ret.xfer(cubes.front());
  cubes.pop_front();
  return ret;
}

//##ModelId=3DD23CCB0339
VCube::Ref VCubeSet::popBack()
{
  Thread::Mutex::Lock lock(mutex_);
  VCube::Ref ret;
  ret.xfer(cubes.back());
  cubes.pop_back();
  return ret;
}

//##ModelId=3DD23C720071
void VCubeSet::pop(VCube::Ref &out)
{
  Thread::Mutex::Lock lock(mutex_);
  out.xfer(cubes.front());
  cubes.pop_front();
}

//##ModelId=3DD23CDB00C2
void VCubeSet::popBack(VCube::Ref &out)
{
  Thread::Mutex::Lock lock(mutex_);
  out.xfer(cubes.back());
  cubes.pop_back();
}

//##ModelId=3DD4C8A5012B
VCube::Ref VCubeSet::remove(int icube)
{
  Thread::Mutex::Lock lock(mutex_);
  VCube::Ref ret;
  remove(icube,ret);
  return ret;
}

//##ModelId=3DD4C8AE03D6
void VCubeSet::remove(int icube, VCube::Ref& out)
{
  Thread::Mutex::Lock lock(mutex_);
  if( icube >= 0 )
  {
    CI iter;
    for( iter = cubes.begin(); icube > 0; icube-- )
      iter++;
    out.xfer(*iter);
    cubes.erase(iter);
  }
  else
  {
    RCI iter;
    for( iter = cubes.rbegin(); icube < -1; icube++ )
      iter++;
    out.xfer(*iter);
    cubes.erase(iter.base());
  }      
}

//##ModelId=3DC672CA0323
CountedRefTarget* VCubeSet::clone(int flags, int depth) const
{
  return new VCubeSet(*this,flags,depth);
}

//##ModelId=3DC672E10339
int VCubeSet::fromBlock(BlockSet& set)
{
  Thread::Mutex::Lock lock(mutex_);
  int bc = 1;
  cubes.clear();
  // get header block
  FailWhen( set.empty(),"invalid set" );
  BlockRef hdrblock = set.pop();
  FailWhen( hdrblock->size() != sizeof(HeaderBlock),"invalid block" );
  const HeaderBlock * phdr = hdrblock->pdata<HeaderBlock>();
  int expect_bc = BObj::checkHeader(phdr);
  cubes.resize(phdr->ncubes);
  for( CI iter = cubes.begin(); iter != cubes.end(); iter++ )
  {
    VCube *pcube = new VCube;
    (*iter) <<= pcube;
    bc += pcube->fromBlock(set);
  }
  FailWhen(bc!=expect_bc,"block count mismatch in header");
  return bc;
}

//##ModelId=3DC672EB001E
int VCubeSet::toBlock(BlockSet &set) const
{
  Thread::Mutex::Lock lock(mutex_);
  int bc = 1;
  // push out a header block
  SmartBlock *pb = new SmartBlock(sizeof(HeaderBlock));
  set.push(BlockRef(pb));
  // convert cubes
  for( CCI iter = cubes.begin(); iter != cubes.end(); iter++ )
    bc += iter->deref().toBlock(set);
  // fill header
  HeaderBlock *hdr = pb->pdata<HeaderBlock>();
  BObj::fillHeader(hdr,bc);
  hdr->ncubes = cubes.size();
  return bc;
}

//##ModelId=3DF9FDD20007
string VCubeSet::sdebug ( int detail,const string &prefix,
                            const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"CI:VCubeSet",this);
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
       out += (*iter).sdebug(detail-1,prefix);
    }
  }
  return out;
}

};
