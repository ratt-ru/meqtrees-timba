//# Resampler.cc: resamples result resolutions
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

#include <MeqNodes/Resampler.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/ResampleMachine.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>


namespace Meq {

const HIID FFlagDensity = AidFlag|AidDensity;

//##ModelId=400E5355029C
Resampler::Resampler()
: Node(1), // 1 child expected
  flag_mask(-1),flag_bit(0),flag_density(0.5)
{}

//##ModelId=400E5355029D
Resampler::~Resampler()
{}

void Resampler::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
//  rec[FIntegrate].get(integrate,initializing);
  rec[FFlagMask].get(flag_mask,initializing);
  rec[FFlagBit].get(flag_bit,initializing);
  rec[FFlagDensity].get(flag_density,initializing);
}

int Resampler::getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &request,bool)
{
  Assert(childres.size()==1);
  const Result &chres = *( childres.front() );
  const Cells &incells = chres.cells();
  const Cells &outcells = request.cells();
  // create resampler
  ResampleMachine resampler(outcells,incells);
  // return child result directly if nothing is to be done
  if( resampler.isIdentical() )
  {
    resref.copy(childres.front());
    return 0;
  }
  // do the resampling  
  resampler.setFlagPolicy(flag_mask,flag_bit,flag_density);
  int nvs = chres.numVellSets();
  Result & result = resref <<= new Result(request,nvs,chres.isIntegrated());
  for( int ivs=0; ivs<nvs; ivs++ )
  {
    VellSet::Ref ref;
    resampler.apply(ref,chres.vellSetRef(ivs),chres.isIntegrated());
    result.setVellSet(ivs,ref);
  }
  return 0;
}

} // namespace Meq
