//# LMN.cc: Calculate source LMN from source position and phase center
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

#include <MeqNodes/LMN.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

using namespace VellsMath;

const HIID child_labels[] = { AidRA|0,AidDec|0,AidRA,AidDec };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

using Debug::ssprintf;

//##ModelId=400E535502D1
LMN::LMN()
: CompoundFunction(num_children,child_labels)
{
}

//##ModelId=400E535502D2
LMN::~LMN()
{}

void LMN::evalResult (std::vector<Vells> &res,const std::vector<const Vells*> &values,const Cells &)
{
  // phase center pos
  #define vra0   (*(values[0]))
  #define vdec0  (*(values[1]))
  // source pos
  #define vra    (*(values[2]))
  #define vdec   (*(values[3]))
  // outputs
  #define L res[0]
  #define M res[1]
  #define N res[2]
  
  L = cos(vdec) * sin(vra-vra0);
  L.makeNonTemp(); // just in case
  M = sin(vdec) * cos(vdec0) - cos(vdec) * sin(vdec0) * cos(vra-vra0);
  M.makeNonTemp();
  N = sqrt(1 - sqr(L) - sqr(M));
  N.makeNonTemp();
}

//##ModelId=400E535502D6
int LMN::getResult (Result::Ref &resref, 
                    const std::vector<Result::Ref> &childres,
                    const Request &request,bool newreq)
{
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  lockMutexes(child_reslock,childres);
  const int expect_nvs[]        = {1,1,1,1};
  const int expect_integrated[] = {0,0,0,0};
  Assert(int(childres.size()) == num_children);
  vector<const VellSet *> child_vs(4);
  // Check that child results are all OK (no fails, expected # of vellsets per child)
  if( checkChildResults(resref,child_vs,childres,expect_nvs,
        expect_integrated) == RES_FAIL )
    return RES_FAIL;
  
  // allocate proper output result (integrated=false)
  Result &result = resref <<= new Result(3,false);
  result.setCells(childres[0]->cells());
  // fill it
  computeValues(result,child_vs);
  return 0;
}

} // namespace Meq
