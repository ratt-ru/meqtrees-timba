//# WSum.cc: Weighted sum of 2 or more nodes
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

#include <MeqNodes/WSum.h>

namespace Meq {    


//##ModelId=3F86886E028F
WSum::WSum()
{}

//##ModelId=3F86886E0293
WSum::~WSum()
{}

void WSum::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Function::setStateImpl(rec,initializing);
  // get/init stddev parameter
  if(!( rec[FWeights].get_vector(weights)) )
    {
      weights.push_back(1.);
      cdebug(3)<<"warning: no weights given, using default 1"<<endl;
      

    }
  
  if(weights.size()>1 && weights.size()<numChildren())
    cdebug(3)<<"Size of weightvector different from number of children, assume 0 for missing weights";
}

//##ModelId=400E531702FD
//needs to be implemented, do not send request to children with weight 0

int WSum::pollChildren (std::vector<Result::Ref> &child_results,
                        Result::Ref &resref,
                        const Request &req)
{
  return Node::pollChildren(child_results,resref,req);
}




Vells WSum::evaluate (const Request& req, const LoShape& shape,
                     const vector<const Vells*>& values)
{

  int nrw=weights.size();
  int allsame =0;
  if(nrw<numChildren()){

       if(nrw==1) allsame=1;//if exactly 1 weight is given, assume all the same
       //otherwise, assume weights = 0 for children without weight
     }
 
  if( values.empty() || nrw<=0)
    return Vells(0.);
  Vells result((*values[0])*weights[0]);
  for( int i=1; i<values.size()&&(allsame || i<nrw); i++ )
    if(!allsame)
      result += (*(values[i]))*weights[i];
    else
      result += (*(values[i]))*weights[0];
      
  return result;
}


} // namespace Meq
