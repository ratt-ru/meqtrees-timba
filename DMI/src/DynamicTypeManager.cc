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

#include "DynamicTypeManager.h"

namespace DMI
{    
    
DefineRegistry(DynamicTypeManager,0);

ObjRef DynamicTypeManager::construct (TypeId tid, BlockSet& bset)
{
  if( bset.empty() )
    return ObjRef(construct(tid));
  if( tid == 0 )
    tid = static_cast<const BObj::Header *>(bset.front()->data())->tid;
  BObj * pobj = construct(tid);
  if( pobj )
  {
    ObjRef ref(pobj);
    pobj->fromBlock(bset);
    return ref;
  }
  return ObjRef();
}

//##ModelId=3BE96C5F03A7
BObj * DynamicTypeManager::construct (TypeId tid, BlockSet& bset, int n)
{
  if( tid == 0 )
    tid = static_cast<const BObj::Header *>(bset.front()->data())->tid;
  BObj *obj = construct(tid,n);
  for( int i=0; i<(n?n:1); i++ )
    obj[i].fromBlock(bset);
  return obj;
}

//##ModelId=3BE96C7402D5
BObj * DynamicTypeManager::construct (TypeId tid, int n)
{
  cdebug1(2)<<"DynTypeMgr: constructing "<<tid.toString();
  if( n ) 
    cdebug1(2)<<"["<<n<<"]";
  cdebug1(2)<<": ";
  PtrConstructor ptr = registry.find(tid);
  FailWhen( !ptr,"Unregistered type "+tid.toString() );
  BObj *obj = (*ptr)(n);
  dprintf1(2)(" @%p\n",obj);
  return obj;
}

//##ModelId=3BF905EE020E
bool DynamicTypeManager::isRegistered (TypeId tid)
{
  return registry.find(tid) != 0;
}


};
