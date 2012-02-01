//# GaussNoise.cc: Give Gauss noise
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

#include <stdlib.h>

#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/GaussNoise.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>

namespace Meq {    

const HIID FMean = AidMean;
const HIID FStdDev = AidStdDev;
const HIID FSeed = AidSeed;
const HIID FComplex = AidComplex;
const HIID child_labels[] = { AidMean,AidStdDev };


//##ModelId=400E535502AC
GaussNoise::GaussNoise()
    : mean_(0),stddev_(1.0),generator_(0,stddev_),complex_(false),
    NoiseNode(2,child_labels,0)
{ 
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
  Thread::Mutex::Lock lock(RndGen::mutex);
  generator_ = RndGen::Normal<double>(0,stddev_);
}

//##ModelId=400E535502AD
GaussNoise::~GaussNoise()
{}

void GaussNoise::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  NoiseNode::setStateImpl(rec,initializing);
  // get/init stddev parameter
  // if one was supplied, reinitialize generator
  if(  rec[FStdDev].get(stddev_,initializing) )
    generator_ = RndGen::Normal<double>(0,stddev_);
  int seed;
  // if seed was supplied, reseed generator
  if( rec[FSeed].get(seed,initializing) )
    generator_.seed((unsigned int) seed);
  rec[FMean].get(mean_,initializing);
  rec[FComplex].get(complex_,initializing);
}

Vells GaussNoise::fillNoise (const Vells::Shape &shape,const std::vector<std::vector<const Vells *> > &children)
{
  // lock mutex to ensure generators are not broken by threads
  Thread::Mutex::Lock lock(RndGen::mutex);
  
  // Get standard deviation from child 2 (mean is handled separately below)
  // Note that I've swapped the children around, as it is handier.
  // If child 2 is not present, reuse old generator initialized previously
  if( children.size() > 1 )
  {
    const Vells & sdv = *(children[1][0]);
    FailWhen(!sdv.isScalar() || !sdv.isReal(),"standard deviation must be a real scalar");
    double sd = sdv.as<double>();
    // if standard deviation changes, create a new generator
    // (if it doesn't, we save some cpu time by reusing the current one)
    if( sd != stddev_ )
      generator_ = RndGen::Normal<double>(0,stddev_=sd);
  }
  // Get standard deviation from child 2 (mean is handled separately below)
  // Note that I've swapped the children around, as it is handier.
  // If child 2 is not present, reuse old generator initialized previously
  Vells meanvells;
  if( children.size() > 0 )
    meanvells = *(children[0][0]);
   
  if( complex_ )
  {
    Vells result(make_dcomplex(0),shape,false);
    // now simply loop over all elements of the output vells -- 
    // we don't really care about its shape, we just fill them all with 
    // numbers from the generator
    for( dcomplex *ptr = result.begin<dcomplex>(); ptr != result.end<dcomplex>(); ptr++ )
      *ptr = mean_ + make_dcomplex(generator_.random(),generator_.random());
    result += meanvells;
    return result;
  }
  else
  {
    Vells result(0.0,shape,false);
    double mean = creal(mean_);
    // now simply loop over all elements of the output vells -- 
    // we don't really care about its shape, we just fill them all with 
    // numbers from the generator
    for( double *ptr = result.begin<double>(); ptr != result.end<double>(); ptr++ )
      *ptr = mean + generator_.random();
    result += meanvells;
    return result;
  }
}

} // namespace Meq
