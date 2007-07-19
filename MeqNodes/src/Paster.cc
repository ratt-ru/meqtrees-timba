//# Paster.cc: Selects result planes from a result set
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#include <MeqNodes/Paster.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

const HIID FMulti = AidMulti;

//##ModelId=400E5355022C
Paster::Paster()
    : Node(2),multi_(false) // exactly 1 child expected
{}

//##ModelId=400E5355022D
Paster::~Paster()
{}

//##ModelId=400E53550233
void Paster::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FIndex].get_vector(selection_,initializing);
  rec[FMulti].get(multi_,initializing);
  
}

//##ModelId=400E53550237
int Paster::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childref,
                         const Request &request,bool)
{
  resref = childref[0];
  // empty selection: simply return child result 1
  if( selection_.empty() )
    return 0;
  const Result &childres = *childref[1];
  int nvs = resref->numVellSets();
  int nvs1 = childres.numVellSets();
  int nsel = selection_.size();
  // multiple-selection mode
  if( multi_ || nsel == 1 )
  {
    if( nvs1 != nsel )
    {
      Throw(ssprintf("size of selection (%d) does not match size of Result to be pasted",nsel,nvs1));
    }
    else
    {
      Result &result = resref();
      // select results from child set
      for( int i=0; i<nsel; i++ )
      {
        int isel = selection_[i];
        if( isel<0 || isel>=nvs )
        {
          Throw(ssprintf("invalid selection index %d for Result of %d VellSet(s)",isel,nvs));
        }
        else
          resref().setVellSet(isel,childres.vellSet(i));
      }
    }
  }
  else // tensor selection or slicing mode
  {
    FailWhen(resref->tensorRank()!=nsel,ssprintf("pasted Result rank %d, index size is %d",resref->tensorRank(),nsel));
    // check selection, and figure out shaped
    const LoShape & dims = resref->dims();
    LoShape shp=dims,shp0=dims,strides=dims;
    int rank = dims.size();
    bool slice = false;
    int strd = 1;
    int offset = 0;
    // work out shape of slice, strides, and offset of slice start
    for( int i=shp.size()-1; i>=0; i-- )
    {
      FailWhen(selection_[i] >= shp[i],ssprintf("selection element #%d out of range",i));
      // see if we're slicing along this axis
      if( selection_[i] < 0 )
        slice = true;
      else
      {
        shp[i] = 1;
        shp0[i] = 0;
        if( !slice )
          rank = i;
        offset += selection_[i]*strd;
      }
      // set stride for this axis
      strides[i] = strd;
      strd *= dims[i];
    }
    // shp now contains the shape of the selection (including any
    // slices), and rank is the maximal non-trivial dimension
    
    // single element selected
    if( rank == 0 ) 
    {
      FailWhen(childres.numVellSets()!=1,"shape of pasted Result does not match shape of selection");
      resref().setVellSet(offset,childres.vellSet(0));
    }
    // else extract full slice
    else
    {
      // shp contains 1's for axes where an element is selected,
      // and the full size where a slice is needed.
      // shp0 is the same, but contains 0s for selected axis.
      // rank is the highest slicing axis+1.
      shp.resize(rank);
      // child result better have the same shape
      FailWhen(childres.dims()!=shp,"shape of pasted Result does not match shape of selection");
      Result &result = resref();
      int nout = shp.product();
      // calculate offset to start of slice
      for( int i=0; i<nout; i++ )
      {
        result.setVellSet(offset,childres.vellSet(i));
        // update offset
        for( int idim = rank-1; idim>=0; idim-- )
          if( shp0[idim] )
          {
            offset += strides[idim]; // advance along this axis
            if( --shp0[idim] )       // still something to go? break
              break;
            else                     // reached end of axis, reset and go to next
              shp0[idim] = shp[idim]; 
          }
      }
    }
  }
  // check that shapes are still valid (since we may have pasted in
  // a child result of a conflicting shape)
  resref().verifyShape();
  
  return 0;
}

} // namespace Meq
