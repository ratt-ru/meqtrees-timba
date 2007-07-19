//# Transpose.cc: Selects result planes from a result set
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

#include <MeqNodes/Transpose.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

const HIID FConj = AidConj;

//##ModelId=400E5355022C
Transpose::Transpose()
    : Node(1),conj_(false) // exactly 1 child expected
{}

//##ModelId=400E5355022D
Transpose::~Transpose()
{}

//##ModelId=400E53550233
void Transpose::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FConj].get(conj_,initializing);
}

void Transpose::conjugate (VellSet &vs)
{
  using VellsMath::conj;
  
  if( !vs.hasValue() )
    return;
  vs.setValue(new Vells(conj(vs.getValue())));
  
  if( vs.numSpids() )
  {
    for( int i=0; i<vs.numPertSets(); i++ )
      for( int j=0; j<vs.numSpids(); j++ )
        vs.setPerturbedValue(j,new Vells(conj(vs.getPerturbedValue(j,i))),i);
  }
}

//##ModelId=400E53550237
int Transpose::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childref,
                         const Request &request,bool)
{
  resref = childref[0];
  int rank = resref->tensorRank();
  FailWhen(rank>2,"illegal tensor rank in transpose");
  int nvs = resref->numVellSets();
  if( rank == 1 )
  {
    LoShape dims(1,resref->numVellSets());
    resref().setDims(dims);
  }
  else if( rank == 2 )
  {
    const Result &chres = *childref[0];
    int nx = chres.dims()[0], 
        ny = chres.dims()[1];
    if( nx == 1 ) // a 1xN element -- just reshape
      resref().setDims(LoShape(ny));
    else
    {
      Result &result = resref();
      result.setDims(LoShape(ny,nx));
      int offs = 0;
      for( int i=0; i<ny; i++ )
        for( int j=0; j<nx; j++,offs++ )
          result.setVellSet(offs,chres.vellSet(j*ny+i));
    }
  }
  // NOP for scalar (rank=0)
  
  // conjugate as needed
  if( conj_ )
  {
    Result &result = resref();
    for( int i=0; i<nvs; i++ )
      conjugate(result.vellSetWr(i));
  }
  
  return 0;
}

} // namespace Meq
