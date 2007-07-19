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

#include "RequestId.h"
#include "MeqVocabulary.h"

using namespace DMI;
    
// const std::map<HIID,int> & Meq::defaultSymdepMasks ()
// {
//   static std::map<HIID,int> masks;
//   static Thread::Mutex mutex;
//   Thread::Mutex::Lock lock(mutex);
//   if( masks.empty() )
//   {
//     masks[FParmValue]  = RQIDM_VALUE;
//     masks[FResolution] = RQIDM_RESOLUTION;
//     masks[FDomain]     = RQIDM_DOMAIN;
//     masks[FDataset]    = RQIDM_DATASET;
//   }
//   return masks;
// }
    
void Meq::RqId::maskSubId (RequestId &id,int mask)
{
  // null mask: clear everything
  if( !mask )
  {
    id = AtomicID(0);
    return;
  }
  HIID::iterator iter = id.begin();
  // ... until we run out of bits, or get to the start of BOTH ids
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != id.end(); 
       m1<<=1,iter++ )
  {
    if( !(mask&m1) )
      *iter = 0;
  }
}

void Meq::RqId::incrSubId (RequestId &id,int mask)
{
  // null mask: do nothing
  if( !mask )
    return;
  // find MSB of mask
  uint msb=0;
  for( int m1=mask; m1 != 0; m1 >>= 1 )
    msb++;
  // if request ID is shorter, resize
  if( id.size() < msb )
    id.resize(msb);
  // start from end 
  HIID::iterator iter = id.begin();
  // ... until we run out of bits, or get to the start of the id
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != id.end(); 
       m1<<=1,iter++ )
  {
    if( mask&m1 )
      *iter = (*iter).id()+1;
  }
}

void Meq::RqId::setSubId (RequestId &id,int mask,int value)
{
  // null mask: do nothing
  if( !mask )
    return;
  // find MSB of mask
  uint msb=0;
  for( int m1=mask; m1 != 0; m1 >>= 1 )
    msb++;
  // if request ID is shorter, resize
  if( id.size() < msb )
    id.resize(msb);
  HIID::iterator iter = id.begin();
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != id.end(); 
       m1<<=1,iter++ )
  {
    if( mask&m1 )
      *iter = value;
  }
}

    
bool Meq::RqId::maskedCompare (const RequestId &id1,const RequestId &id2,int mask)
{
  // null mask: comparison always succeeds
  if( !mask )
    return true;
  // null id always fails comparison
  if( id1.empty() || id2.empty() )
    return false;
  // start comparing from start of each ID
  HIID::const_iterator iter1 = id1.begin();
  HIID::const_iterator iter2 = id2.begin();
  // ... until we run out of bits, or get to the end of BOTH ids
  for(  int m1=1; 
        m1 < (1<<RQIDM_NBITS) && (iter1 != id1.end() || iter2 != id2.end()); 
        m1<<=1 )
  {
    // once we run out of indices in either ID, assume 0
    AtomicID x1 = iter1 != id1.end() ? *(iter1++) : AtomicID(0);
    AtomicID x2 = iter2 != id2.end() ? *(iter2++) : AtomicID(0);
    if( mask&m1 && x1 != x2 )
      return false;
  }
  return true;
}

int Meq::RqId::diffMask (const RequestId &id1,const RequestId &id2)
{
  int mask = 0;
  HIID::const_iterator iter1 = id1.begin();
  HIID::const_iterator iter2 = id2.begin();
  // ... until we run out of bits, or get to the end of BOTH ids
  for(  int m1=1; 
        m1 < (1<<RQIDM_NBITS) && (iter1 != id1.end() || iter2 != id2.end()); 
        m1<<=1 )
  {
    // once we run out of indices in either ID, assume 0
    AtomicID x1 = iter1 != id1.end() ? *(iter1++) : AtomicID(0);
    AtomicID x2 = iter2 != id2.end() ? *(iter2++) : AtomicID(0);
    if( x1 != x2 )
      mask |= m1;
  }
  return mask;
}
