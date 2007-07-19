//# WSum.cc: Weighted sum of 2 or more nodes
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

#include <MeqNodes/WSum.h>

namespace Meq {    


//##ModelId=3F86886E028F
WSum::WSum()
  : weights(1,1.)
{
}

//##ModelId=3F86886E0293
WSum::~WSum()
{}

void WSum::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Function::setStateImpl(rec,initializing);
  
  if( rec[FWeights].get_vector(weights) )
  {
    // empty vector -- use [1.]
    if( weights.empty() )
      weights.resize(1,1.);
    
    // ensure we have same # of weights as children, fill in 0. for missing weights
    if( weights.size() > 1 )
    {
      weights.resize(numChildren(),0.0);
      // disable children with 0 weight
      for( int i=0; i<numChildren(); i++ )
        children().enableChild(i,weights[i]!=0.);
    }
    else // single weight given, enable all children
    {
      for( int i=0; i<numChildren(); i++ )
        children().enableChild(i);
    }
  }
}

Vells WSum::evaluate (const Request& req, const LoShape& shape,
                     const vector<const Vells*>& values)
{
  size_t nrw=weights.size();
  bool allsame = ( nrw==1 );
 
  if( values.empty() || nrw<=0 )
    return Vells(0.);
  
  Vells result;
  if( weights[0] != 0. )
    result = (*values[0])*weights[0];
  else
    result = Vells(0.);
  
  for( size_t i=1; i<values.size(); i++ )
  {
    double w = allsame ? weights[0] : weights[i];
    if( w != 0.0 )
      result += (*(values[i]))*w;
  }
  
  return result;
}


} // namespace Meq
