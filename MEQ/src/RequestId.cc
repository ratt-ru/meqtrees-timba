#include "RequestId.h"

bool Meq::maskedCompare (const RequestId &a,const RequestId &b,int mask)
{
  if( mask&RES_DEP_ITER && getIterId(a) != getIterId(b) )
    return false;
  if( mask&RES_DEP_CONFIG && getConfigId(a) != getConfigId(b) )
    return false;
  if( mask&RES_DEP_DOMAIN && getDomainId(a) != getDomainId(b) )
    return false;
  return true;
}
