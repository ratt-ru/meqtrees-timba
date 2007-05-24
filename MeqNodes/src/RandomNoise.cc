//# RandomNoise.cc: Give Random values
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

#include <stdlib.h>

#include <MeqNodes/AID-MeqNodes.h>
#include <MeqNodes/RandomNoise.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>

namespace Meq {    

const HIID FSeed = AidSeed;

//##ModelId=400E535502AC
RandomNoise::RandomNoise()
{ 
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

//##ModelId=400E535502AD
RandomNoise::~RandomNoise()
{}

//##ModelId=400E535502AF
//void RandomNoise::init (DMI::Record::Ref::Xfer &initrec, Forest* frst)
//{
//  Node::init(initrec,frst);
  // FailWhen(numChildren(),"RandomNoise node cannot have children");
//}

void RandomNoise::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  int seed;
  if( rec[FSeed].get(seed,initializing) )
  {
    // if seed was supplied, reseed generator
    srandom((unsigned int) seed);
  }
}

//##ModelId=400E535502B5
int RandomNoise::getResult (Result::Ref &resref, 
                     const std::vector<Result::Ref> &childres,
                     const Request &request,bool newreq)
{
  //
  // Get values from child 1 and 2.
  // - Child 1 is supposed to have the minimun value for the the random numbers.
  // - Child 2 is supposed to have the maximun value
  // - range is the requested range (max - min)
  //
  const Vells& vra  = childres[0]->vellSet(0).getValue();
  double MinVal = vra.as<double>();

  const Vells& vrb  = childres[1]->vellSet(0).getValue();
  double MaxVal = vrb.as<double>();

  double range = MaxVal - MinVal;
//  srandom(123);

  //
  // Create the cells.
  //
  const Cells& cells = request.cells();
  //
  // Create result object and attach to the ref that was passed in.
  //
  resref <<= new Result(1);                 // 1 plane
  VellSet& vs = resref().setNewVellSet(0);  // create new object for plane 0

  //
  if( cells.isDefined(Axis::TIME) && cells.isDefined(Axis::FREQ))
  {
    Vells::Shape shape;
    Axis::degenerateShape(shape,cells.rank());

    //
    // nt = shape of TIME axis
    // nf = shape of FREQ axis
    //
    int nt = shape[Axis::TIME] = cells.ncells(Axis::TIME);
    int nf = shape[Axis::FREQ] = cells.ncells(Axis::FREQ);
    Vells & vells = vs.setValue(new Vells(0,shape,false));

    //
    // make a temp storage for the random numbers
    //
    double tmp[nf][nt];
    double Scale = RAND_MAX;   // max. number that comes from the random generator

    //
    // Create the random numbers
    // Divide by Scale -> range is 0-1
    // Multiply by range -> range is 0-range
    // Add to min value -> range is min-max
    //
    for (int i = 0; i < nt; i++){
      for (int j = 0; j < nf; j++){
	tmp[j][i] = random();
	tmp[j][i] /= Scale;
	tmp[j][i] = tmp[j][i] * range + MinVal;
      }
    }

    //
    // copy to vells
    //
    memcpy(vells.realStorage(), tmp, nt*nf*sizeof(double));
  } else
    vs.setValue(new Vells(0.));

  return 0;
}

} // namespace Meq
