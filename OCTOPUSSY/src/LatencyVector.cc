#include "Common/Debug.h"
#include "OCTOPUSSY/LatencyVector.h"
#include "DMI/Packer.h"    
#include <unistd.h>
#include <math.h>
   
// returns sum of all values
//##ModelId=3DB958F300F8
Timestamp LatencyVector::total () const
{ 
  Timestamp tot(0,0);
  for( CVEI iter = tms.begin(); iter != tms.end(); iter++ )
    tot += iter->first;
  return tot;
}

// adds two latency vectors together
//##ModelId=3DB958F300FA
LatencyVector & LatencyVector::operator += ( const LatencyVector & other )
{
  if( tms.size() )
  {
    FailWhen(other.tms.size() != tms.size(),
        "incompatible latency vectors [" +
        toString() + "] and [" + other.toString() + "]" );
    VEI iter = tms.begin();
    CVEI iter2 = other.tms.begin();
    for( ; iter2 != other.tms.end(); iter++,iter2++ )
    {
      FailWhen(iter->second != iter2->second,
        "incompatible latency vectors [" +
        toString() + "] and [" + other.toString() + "]" );
      iter->first += iter2->first;
    }
  }
  else // null vector -- simply copy other over
  {
    tms = other.tms;
  }
  return *this;
}
    
// divides latency vector by some value
//##ModelId=3DB958F3010D
LatencyVector & LatencyVector::operator /= ( double x )
{
  for( VEI iter = tms.begin(); iter != tms.end(); iter++ )
    iter->first /= x;
  return *this;
}

// converts latency vector to strings
//##ModelId=3DB958F30120
string LatencyVector::toString() const
{
  string out;
  for( CVEI iter = tms.begin(); iter != tms.end(); iter++ )
    out += iter->second + ":" + iter->first.toString(Timestamp::USEC) + " ";
  out += "(us)";
  return out;
}

// implement the Packer template for a LatencyVector::Entry
template <>
inline size_t Packer<LatencyVector::Entry>::pack (const LatencyVector::Entry& obj, void* block,size_t &nleft)
{
  FailWhen(nleft < sizeof(obj.first) + obj.second.length(),"block too small");
  nleft -= obj.second.length() + sizeof(obj.first);
  *static_cast<Timestamp*>(block) = obj.first;
  return sizeof(obj.first) + 
      obj.second.copy(static_cast<char*>(block)+sizeof(obj.first),string::npos);
}

template <>
inline void Packer<LatencyVector::Entry>::unpack (LatencyVector::Entry& obj, const void* block, size_t sz)
{
  FailWhen(sz < sizeof(obj.first),"block too small");
  obj.first = *static_cast<const Timestamp *>(block);
  sz -= sizeof(obj.first);
  obj.second.assign(static_cast<const char*>(block) + sizeof(obj.first),sz);
}

template <>
inline size_t Packer<LatencyVector::Entry>::packSize (const LatencyVector::Entry& obj)
{
  return sizeof(obj.first) + obj.second.length();
}

//##ModelId=3DB958F30122
size_t LatencyVector::pack (void *block,size_t &nleft) const
{
  Timestamp *bl = static_cast<Timestamp*>(block);
  *bl++ = tms0;
  nleft -= sizeof(tms0);
  return SeqPacker<vector<Entry> >::pack(tms,bl,nleft);
}

//##ModelId=3DB958F30148
void LatencyVector::unpack (const void *block,size_t sz)
{
  FailWhen(sz < sizeof(tms0),"block too small");
  const Timestamp *bl = static_cast<const Timestamp*>(block);
  tms0 = *bl++;
  SeqPacker<vector<Entry> >::unpack(tms,bl,sz-sizeof(tms0));
}

//##ModelId=3DB958F3016C
size_t LatencyVector::packSize () const
{
  return sizeof(tms0) + SeqPacker<vector<Entry> >::packSize(tms);
}

