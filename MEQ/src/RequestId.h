#ifndef MeqSERVER_SRC_REQUESTID_H_HEADER_INCLUDED
#define MeqSERVER_SRC_REQUESTID_H_HEADER_INCLUDED
    
#include <DMI/HIID.h>

namespace Meq {   
  
typedef HIID RequestId;

// RequestId
// The request ID is basically a HIID. A "normalized" request ID
// will contain at least three indices.
// The HIID is split up as follows:
//    <domain ID>.<config id>.<iteration id>
// The domain ID may contain more than one element; the other IDs
// are single-element

// -----------------------------------------------------------------------
// get...Id()
// this extracts the component parts from a Request ID
// -----------------------------------------------------------------------
inline int getIterId (const RequestId &rqid)
{ 
  int n = rqid.size();
  return n>0 ? rqid[n-1].id() : 0;  
}
    
inline int getConfigId (const RequestId &rqid)
{ 
  int n = rqid.size();
  return n>1 ? rqid[n-2].id() : 0;
}

inline HIID getDomainId (const RequestId &rqid)
{ 
  int n = rqid.size();
  return n>2 ? rqid.subId(0,n-3) : RequestId();
}

// -----------------------------------------------------------------------
// normalizeRequestId()
// this "normalizes" a request Id, assuring of at least three elements
// first version normalizes in place
// -----------------------------------------------------------------------
inline RequestId & normalizeRequestId (RequestId &rqid)
{
  for( int i=rqid.size(); i<3; i++ )
    rqid |= AtomicID(0);
  return rqid;
}

// second version returns normalized ID by value
inline RequestId makeNormalRequestId (const RequestId &rqid)
{
  RequestId ret = rqid;
  return normalizeRequestId(ret);
}

// -----------------------------------------------------------------------
// makeRequestId()
// creates a request ID from component parts
// -----------------------------------------------------------------------
inline RequestId makeRequestId(const HIID &dom_id,int config_id=0,int iter_id=0)
{
  return dom_id|AtomicID(config_id)|AtomicID(iter_id);
}

// -----------------------------------------------------------------------
// set...Id()
// this sets the component parts of a Request ID
// -----------------------------------------------------------------------
inline RequestId & setDomainId (RequestId &rqid,const HIID &domid)
{
  return rqid = makeRequestId(domid,getConfigId(rqid),getIterId(rqid));
}

inline RequestId & setConfigId (RequestId &rqid,int conf_id)
{
  normalizeRequestId(rqid);
  rqid[rqid.size()-2] = conf_id;
  return rqid;
}

inline RequestId & setIterationId (RequestId &rqid,int iter_id)
{
  normalizeRequestId(rqid);
  rqid.back() = iter_id;
  return rqid;
}

inline RequestId & nextIterationId (RequestId &rqid)
{
  normalizeRequestId(rqid);
  rqid.back() = AtomicID(rqid.back().id()+1);
  return rqid;
}

// -----------------------------------------------------------------------
// dependency flags
// -----------------------------------------------------------------------

typedef enum 
{
  // bitmask of result dependencies
  RES_DEPEND_MASK  = 0xFFFF00, // full dependency mask
  RES_DEPEND_NBITS = 16,       // number of bits in dependency mask
  RES_DEPEND_LSB   = 0x100,    // LSB of dependency mask

  // predefine some constants for application-specific dependencies
  RES_DEP_VOLATILE = 0x100,    // result is volatile (depends on external events)
  RES_DEP_DOMAIN   = 0x200,    // depends on domain
  RES_DEP_CONFIG   = 0x400,    // depends on config
  RES_DEP_ITER     = 0x800     // depends on iteration

} ResultDeps;

// for generic dependency treatment:
// returns bit indicating dependency on request ID index #n
inline int RES_DEP (int n)
{ 
  return RES_DEPEND_LSB<<n; 
}
    
// -----------------------------------------------------------------------
// maskedCompare()
// Compares two IDs using a mask -- i.e., only the components with
// corresponding RES_DEP_xxx bits ion the mask are compared
// -----------------------------------------------------------------------
bool maskedCompare (const RequestId &a,const RequestId &b,int mask);

};
#endif
