//# MaxLocation.cc: Calculate source MaxLocation from source position and phase center
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
//# $Id: MaxLocation.cc 3568 2006-05-15 14:11:19Z smirnov $

#include <MeqNodes/MaxLocation.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

using namespace VellsMath;


const HIID FDomain = AidDomain;

using Debug::ssprintf;

//##ModelId=400E535502D1
MaxLocation::MaxLocation()
: TensorFunction(1)
{
}

//##ModelId=400E535502D2
MaxLocation::~MaxLocation()
{}


LoShape MaxLocation::getResultDims (const vector<const LoShape *> &input_dims)
{
  const LoShape &dim = *input_dims[0];
  std::cout<<dim<<std::endl;

  std::cout<<"Dims "<<std::endl;
  //calculate dims depending on the size of cells
  // result is a 3-vector
  return LoShape((cells_)->rank());
}
    

void MaxLocation::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  std::cout<<"Cells "<<std::endl;
  const Cells &cells =  request.cells();
  //remember cells
  const Result &chres = *( childres.front() );
  cells_ <<= new Cells(chres.cells());
  FailWhen(!cells.isDefined(Axis::TIME),"Meq::MaxLocation: no time axis in request, can't compute AzEls");
  ref.attach(cells);
}


void MaxLocation::evaluateTensors (std::vector<Vells> & out,   
     const std::vector<std::vector<const Vells *> > &args )
{

  std::cout<<"Eval "<<std::endl;
  // thanks to checks in getResultDims(), we can expect all 
  // vectors to have the right sizes
  
  //get input vells
  const Vells &val= *(args[0][0]);
  std::cout<<val.shape()<<std::endl;
  std::cout<<(cells_)->shape()<<std::endl;
  
  int dim=val.shape().size();
  //get data as blitz++ array
  double *indata=const_cast<double*>(val.realStorage());
  if (dim==1) {

  } else if (dim==2) {

  } else if (dim==3) {

  } else if (dim==4) {
    blitz::Array<double,4> A(indata,val.shape(),blitz::neverDeleteData);
    blitz::TinyVector<int,4> maxi=blitz::maxIndex(A);
    std::cout<<"Maxi "<<maxi<<std::endl;
    for (int ii=0; ii<4; ii++) {
     blitz::Array<double,1> xx=cells_->center(ii);
     std::cout<<xx<<std::endl;
     if (xx.size()>0) {
     out[ii]=Vells(xx(maxi(ii)),blitz::shape(1));
     std::cout<<xx(maxi(ii))<<std::endl;
     } else {
      //no cells
     }
    }
  }

}

} // namespace Meq
