//# Composer.cc: Selects result planes from a result set
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
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
  // check that integrated property matches
  bool integrated = childres[0]->isIntegrated();
  for( int i=1; i<numChildren(); i++ )
  {
    FailWhen( childres[i]->isIntegrated() != integrated,
        "'integrated' property of child results is not uniform");
  }
  // compose the result
  Result *presult;
  if( dims_.empty() )
    resref <<= presult = new Result(nres,integrated);
  else
  {
    resref <<= presult = new Result(dims_,integrated);
    FailWhen(presult->numVellSets()!=nres,
             "number of child results does not match tensor dimensions");
  }
  int ires=0;
  const Cells *pcells = 0;
  for( int i=0; i<numChildren(); i++ )
  {
    const Result &chres = *childres[i];
    for( int ivs=0; ivs<chres.numVellSets(); ivs++ )
    {
      const VellSet &vs = chres.vellSet(ivs);
      presult->setVellSet(ires++,vs);
      if( vs.isFail() )
        nfails++;
      else if( vs.isEmpty() )
        nmissing++;
    }
    if( !pcells && chres.hasCells() )
      pcells = &( chres.cells() );
  }
  if( nfails == nres )
    return RES_FAIL;
  if( nmissing == nres )
    return RES_MISSING;
  // apply cells as needed
  if( pcells )
    presult->setCells(pcells);
  // we do not introduce any dependencies
  return 0;
}

} // namespace Meq
