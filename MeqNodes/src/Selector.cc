//# Selector.cc: Selects result planes from a result set
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

#include <MeqNodes/Selector.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {

const HIID FMulti = AidMulti;

//##ModelId=400E5355022C
Selector::Selector()
    : Node(1),multi_(false) // exactly 1 child expected
{}

//##ModelId=400E5355022D
Selector::~Selector()
{}

//##ModelId=400E53550233
void Selector::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FIndex].get_vector(selection_,initializing);
  rec[FMulti].get(multi_,initializing);
}

//##ModelId=400E53550237
int Selector::getResult (Result::Ref &resref,
                         const std::vector<Result::Ref> &childref,
                         const Request &request,bool)
{
  // empty selection: return child result
  if( selection_.empty() )
  {
    resref = childref[0];
    return 0;
  }
  bool fail    = true;  // cleared below later once we have a non-fail selection
  bool missing = true;  // cleared below once we have a non-missing-data selection
  const Result &childres = *childref[0];
  int nvs = childres.numVellSets();
  // multiple-selection mode
  if( multi_ || selection_.size() == 1 )
  {
    Result &result = resref <<= new Result(selection_.size());
    // select results from child set
    for( uint i=0; i<selection_.size(); i++ )
    {
      int isel = selection_[i];
      if( isel<0 || isel>=nvs )
      {
        MakeFailVellSet(result.setNewVellSet(i),
            ssprintf("invalid selection index %d for Result of %d VellSet(s)",
                          isel,nvs));
      }
      else
      {
        const VellSet & vs = childres.vellSet(isel);
        result.setVellSet(i,vs);
        if( !vs.isFail() )
          fail = false;
        if( !vs.isEmpty() )
          missing = false;
      }
    }
  }
  else // tensor selection or slicing mode
  {
    FailWhen(childres.tensorRank()!=int(selection_.size()),ssprintf("child Result rank %d, index size is %d",childres.tensorRank(),selection_.size()));
    // check selection, and figure out shape
    const LoShape & dims = childres.dims();
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
    // shp now contains the output shape of the selection (including any
    // slices), and rank is the maximal non-trivial dimension

    // single element selected
    if( rank == 0 )
    {
      const VellSet &vs = childres.vellSet(offset);
      (resref <<= new Result(1)).
            setVellSet(0,vs);
      if( !vs.isFail() )
        fail = false;
      if( !vs.isEmpty() )
        missing = false;
    }
    // else extract full slice
    else
    {
      // shp contains 1's for axes where an element is selected,
      // and the full size where a slice is needed.
      // shp0 is the same, but contains 0s for selected axis.
      // rank is the highest slicing axis+1.
      shp.resize(rank);
      Result &result = resref <<= new Result(shp);
      int nout = shp.product();
      // calculate offset to start of slice
      for( int i=0; i<nout; i++ )
      {
        const VellSet &vs = childres.vellSet(offset);
        result.setVellSet(i,vs);
        if( !vs.isFail() )
          fail = false;
        if( !vs.isEmpty() )
          missing = false;
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
  // return fail or missing data if needed
  if( fail )
    return RES_FAIL;
  if( missing )
    return RES_MISSING;

  // else add input cells as needed
  if( childres.hasCells() )
    resref().setCells(childres.cells());

  return 0;
}

} // namespace Meq
