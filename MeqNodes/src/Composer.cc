//# Composer.cc: Selects result planes from a result set
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

#include <MeqNodes/Composer.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

//##ModelId=400E53050042
Composer::Composer()
  : Node(-2,0) // at least 1 child must be present
{
  // by default we ignore all fails and missing data
  children().setFailPolicy(AidIgnore);
  children().setMissingDataPolicy(AidIgnore);
  // we can only compose results with the same cells
  setAutoResample(RESAMPLE_FAIL);
}

//##ModelId=400E53050043
Composer::~Composer()
{}

//##ModelId=400E5305004A
void Composer::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  DMI::Record::Hook hdims(rec,FDims);
  if( hdims.type() == Tpbool && !hdims.as<bool>() )
    dims_.clear();
  else
    hdims.get_vector(dims_);
}

//##ModelId=400E5305004F
int Composer::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &request,bool)
{
  // count # of output planes, and # of fails/missing data among them
  int nres = 0, nfails = 0, nmissing = 0;
  for( uint i=0; i<childres.size(); i++ )
    nres += childres[i]->numVellSets();
  // tensor mode enabled when dims_=[0]
  bool tensor_mode = ( dims_.size() == 1 && !dims_[0] );
  Result::Dims dims0;
  int nres0 = 0;
  // if any children are tensors, then they must have the same rank and dims (=dims0).
  // It is possible to mix tensors and scalars, though 
  for( int i=0; i<numChildren(); i++ )
  {
    const Result &chres = *childres[i];
    if( tensor_mode )
    {
      // tensor_mode=true if we've come upon at least one child with a tensor
      // result. Once that happens, start verifying dimensions
      Result::Dims dims = chres.dims();
      if( dims.empty() )
        dims = LoShape(1);
      if( i>0 )
      {
        FailWhen(dims0 != dims,Debug::ssprintf(
            "tensor dimensions of child result %d do not match those of previous children",i));
      }
      else
      {
        dims0 = dims;
        nres0 = dims0.product();
      }
    }
  }
  // compose the result
  Result *presult;
  if( dims_.empty() )
    resref <<= presult = new Result(nres);
  else
  {
    // in tensor mode, result is composed with a new outer tensor dimension 
    // going over children
    if( tensor_mode )
    {
      Result::Dims dims(true,dims0.size()+1);
      dims[0] = childres.size();
      for( uint i=1; i<dims.size(); i++ )
        dims[i] = dims0[i-1];
      resref <<= presult = new Result(dims);
    }
    else // use standard dims
      resref <<= presult = new Result(dims_);
  }
  int ires=0;
  const Cells *pcells = 0;
  for( int i=0; i<numChildren(); i++ )
  {
    const Result &chres = *childres[i];
    // in tensor mode, we have to make sure the right number of vellsets is
    // inserted for, e.g., missing children
    if( tensor_mode )
    {
      // if child has the right number of vellsets already, just copy them over
      if( chres.numVellSets() == nres0 )
      {
        for( int ivs=0; ivs<chres.numVellSets(); ivs++ )
        {
          const VellSet &vs = chres.vellSet(ivs);
          presult->setVellSet(ires++,vs);
          if( vs.isFail() )
            nfails++;
          else if( vs.isEmpty() )
            nmissing++;
        }
      }
      // else fill in tensor dims with repeated scalar vellset
      else if( chres.numVellSets() <= 1 )
      {
        VellSet::Ref vsref;
        if( chres.numVellSets() )
        {
          vsref <<= &( chres.vellSet(0) );
          if( vsref->isFail() )
            nfails += nres0;
        }
        else
        {
          vsref <<= new VellSet;
          nmissing += nres0;
        }
        for( int ivs=0; ivs<nres0; ivs++ )
          presult->setVellSet(ires++,*vsref);
      }
      else
        Throw(Debug::ssprintf("child %d returned an unexpected number of Result planes (%d)",i,chres.numVellSets()));
    }
    // in normal mode, just append child results one after the other
    else
    {
      for( int ivs=0; ivs<chres.numVellSets(); ivs++ )
      {
        const VellSet &vs = chres.vellSet(ivs);
        presult->setVellSet(ires++,vs);
        if( vs.isFail() )
          nfails++;
        else if( vs.isEmpty() )
          nmissing++;
      }
    }
    if( !pcells && chres.hasCells() )
      pcells = &( chres.cells() );
  }
  if( nres )
  {
    if( nfails == nres )
      return RES_FAIL;
    if( nmissing == nres )
      return RES_MISSING;
    // apply cells as needed
    if( pcells )
      presult->setCells(pcells);
  }
  // we do not introduce any dependencies
  return 0;
}

} // namespace Meq
