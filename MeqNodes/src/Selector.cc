//# Selector.cc: Selects result planes from a result set
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

#include <MeqNodes/Selector.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

//##ModelId=400E5355022C
Selector::Selector()
    : Node(1) // exactly 1 child expected
{}

//##ModelId=400E5355022D
Selector::~Selector()
{}

//##ModelId=400E53550233
void Selector::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FIndex].get_vector(selection,initializing);
}

//##ModelId=400E53550237
int Selector::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childref,
                         const Request &request,bool)
{
  // otherwise, select sub-results
  Result &result = resref <<= new Result(selection.size(),request);
  const Result &childres = *childref[0];
  int nvs = childres.numVellSets();
  // select results from child set
  for( uint i=0; i<selection.size(); i++ )
  {
    int isel = selection[i];
    if( isel<0 || isel>=nvs )
    {
      VellSet &vs = result.setNewVellSet(i);
      MakeFailVellSet(vs,
          Debug::ssprintf("selection index %d is out of range (%d results in set)",
                        isel,nvs));
    }
    else
    {
      VellSet::Ref ref = childres.vellSetRef(isel);
      result.setVellSet(i,ref);
    }
  }
  // no additional dependencies
  return 0;
}

} // namespace Meq
