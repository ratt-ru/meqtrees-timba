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

#ifndef MeqSERVER_SRC_REQUESTID_H_HEADER_INCLUDED
#define MeqSERVER_SRC_REQUESTID_H_HEADER_INCLUDED
    
#include <DMI/HIID.h>
#include <MEQ/AID-Meq.h>
    
namespace Meq 
{ 
  
using namespace DMI;
  
// // -----------------------------------------------------------------------
// // dependency flags and symbolic dependencies
// // -----------------------------------------------------------------------
// 
////##Documentation
////## define a default set of dependency masks for nodes that generate
////## requests. These may be overridden via node state
typedef enum
{
//   RQIDM_VALUE       = 0x0001,
//   RQIDM_RESOLUTION  = 0x0002,
//   RQIDM_DOMAIN      = 0x0004,
//   RQIDM_DATASET     = 0x0008,
//   
  RQIDM_NBITS       = 16
} RequestIdMasks;
  
//##Documentation
//## The request ID is basically a HIID of length up to RQIDM_NBITS. Each 
//## index of an rqid maps onto one bit of the rqid mask, starting with 
//## the _first_ index. 
typedef HIID RequestId;
// 
// //=== Some standard symbolic deps
// const HIID FParmValue  = AidParm|AidValue;
// const HIID FResolution = AidResolution;
// // const HIID FDomain     = AidDomain; // already defined in MeqVocabulary
// const HIID FDataset    = AidDataset;
// 
// // -----------------------------------------------------------------------
// // defaultSymdepMasks()
// // returns set of default symdep masks corresponding to RQIDMs above
// // -----------------------------------------------------------------------
// const std::map<HIID,int> & defaultSymdepMasks ();

// utility functions reside in this namespace
namespace RqId
{

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
// setSubId()
// sets all indices whose maskbit is 1 to given value
// -----------------------------------------------------------------------
void setSubId (RequestId &rqid,int mask,int value);

inline RequestId setSubId (const RequestId &rqid,int mask,int value)
{ RequestId res = rqid; setSubId(res,mask,value); return res; }

// -----------------------------------------------------------------------
// maskedCompare()
// Compares two IDs using a mask -- i.e., only indices with a 1 maskbit
// are compared. Returns true if the IDs match
// -----------------------------------------------------------------------
bool maskedCompare (const RequestId &a,const RequestId &b,int mask);

// -----------------------------------------------------------------------
// diffMask()
// Compares two IDs and returns a bitmask with each bit set if IDs
// are different
// -----------------------------------------------------------------------
int diffMask (const RequestId &a,const RequestId &b);

}

};
#endif
