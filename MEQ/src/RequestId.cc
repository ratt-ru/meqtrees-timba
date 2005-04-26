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
  // staqrt from end 
  HIID::reverse_iterator iter = id.rbegin();
  // ... until we run out of bits, or get to the start of BOTH ids
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != id.rend(); 
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
    id.push_front(0,msb-id.size());
  // start from end 
  HIID::reverse_iterator iter = id.rbegin();
  // ... until we run out of bits, or get to the start of the id
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != id.rend(); 
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
    id.push_front(0,msb-id.size());
  // start from end 
  HIID::reverse_iterator iter = id.rbegin();
  // ... until we run out of bits, or get to the start of the id
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != id.rend(); 
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
  // start comparing from end of each ID
  HIID::const_reverse_iterator iter1 = id1.rbegin();
  HIID::const_reverse_iterator iter2 = id2.rbegin();
  // ... until we run out of bits, or get to the start of BOTH ids
  for(  int m1=1; 
        m1 < (1<<RQIDM_NBITS) && (iter1 != id1.rend() || iter2 != id2.rend()); 
        m1<<=1 )
  {
    // once we run out of indices in either ID, assume 0
    AtomicID x1 = iter1 != id1.rend() ? *(iter1++) : AtomicID(0);
    AtomicID x2 = iter2 != id2.rend() ? *(iter2++) : AtomicID(0);
    if( mask&m1 && x1 != x2 )
      return false;
  }
  return true;
}

int Meq::RqId::diffMask (const RequestId &id1,const RequestId &id2)
{
  int mask = 0;
  // start comparing from end of each ID
  HIID::const_reverse_iterator iter1 = id1.rbegin();
  HIID::const_reverse_iterator iter2 = id2.rbegin();
  // ... until we run out of bits, or get to the start of BOTH ids
  for(  int m1=1; 
        m1 < (1<<RQIDM_NBITS) && (iter1 != id1.rend() || iter2 != id2.rend()); 
        m1<<=1 )
  {
    // once we run out of indices in either ID, assume 0
    AtomicID x1 = iter1 != id1.rend() ? *(iter1++) : AtomicID(0);
    AtomicID x2 = iter2 != id2.rend() ? *(iter2++) : AtomicID(0);
    if( x1 != x2 )
      mask |= m1;
  }
  return mask;
}
