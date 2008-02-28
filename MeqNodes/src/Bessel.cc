//# Bessel.cc: Take exponent of a node
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
//# $Id: Bessel.cc 5418 2007-07-19 16:49:13Z oms $

#include <MeqNodes/Bessel.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;


namespace Meq {    

const HIID FOrder= AidOrder;

Bessel::Bessel()
{ order_=0; }

Bessel::~Bessel()
{}

void Bessel::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);

  if(rec[FOrder].get(order_,initializing)) {
#ifdef DEBUG
    cout<<"Bessel Order="<<order_<<endl;
#endif
  }
}


Vells Bessel::evaluate (const Request&,const LoShape & inshape,
		     const vector<const Vells*>& values)
{
  //return exp(*(values[0]));
  const Vells &invl=*(values[0]);
  blitz::Array<double,2> A(const_cast<double*>(invl.realStorage()),inshape);
  Vells outvl(0.0,inshape);
  
  blitz::Array<double,2> B(outvl.realStorage(),inshape);
  if (order_==0) {
    B=blitz::j0(A);
  } else {
    B=blitz::j1(A);
  } 
  return outvl;
}

} // namespace Meq
