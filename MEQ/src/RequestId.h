#ifndef MeqSERVER_SRC_REQUESTID_H_HEADER_INCLUDED
#define MeqSERVER_SRC_REQUESTID_H_HEADER_INCLUDED
    
#include <DMI/HIID.h>
    
namespace Meq {
  
// -----------------------------------------------------------------------
// dependency flags and symbolic dependencies
// -----------------------------------------------------------------------

//##Documentation
//## define a default set of dependency masks for nodes that generate
//## requests. These may be overridden via node state
typedef enum
{
  RQIDM_VALUE       = 0x0001,
  RQIDM_RESOLUTION  = 0x0002,
  RQIDM_DOMAIN      = 0x0004,
  RQIDM_DATASET     = 0x0008,
  
  RQIDM_NBITS       = 16
} RequestIdMasks;
  
//##Documentation
//## The request ID is basically a HIID of length up to RQIDM_NBITS. Each 
//## index of an rqid maps onto one bit of the rqid mask, starting with 
//## the _last_ index. 
typedef HIID RequestId;


// -----------------------------------------------------------------------
// maskSubId()
// Sets to 0 all indices whose maskbit is 0. 
// This essentially returns the "sub-id" corresponding to mask.
// -----------------------------------------------------------------------
void maskSubId (RequestId &rqid,int mask);

inline RequestId maskSubId (const RequestId &rqid,int mask)
{ RequestId res = rqid; maskSubId(res,mask); return res; }

// -----------------------------------------------------------------------
// incrSubId()
// increments all indices whose maskbit is 1.
// -----------------------------------------------------------------------
void incrSubId (RequestId &rqid,int mask);

inline RequestId incrSubId (const RequestId &rqid,int mask)
{ RequestId res = rqid; incrSubId(res,mask); return res; }

// -----------------------------------------------------------------------
// maskedCompare()
// Compares two IDs using a mask -- i.e., only indices with a 1 maskbit
// are compared. Returns true if the IDs match
// -----------------------------------------------------------------------
bool maskedCompare (const RequestId &a,const RequestId &b,int mask);

};
#endif
