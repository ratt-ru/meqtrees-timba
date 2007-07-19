//# WMean.cc: Weighted average of 2 or more nodes
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

#include <MeqNodes/WMean.h>

namespace Meq {    


//##ModelId=3F86886E028F
WMean::WMean()
{}

//##ModelId=3F86886E0293
WMean::~WMean()
{}

void WMean::NormWeights(){
  double sum=0.;
  int nrw=weights.size();

  //if no weights, or only 1 given set all weights to 1./numchildren
  if(nrw<=1) 
    {
      if(nrw<=0)
	weights.push_back(1./numChildren());
      if(nrw==1) weights[0]=1./numChildren();
     return;
    }

  else
    {
      for(int i=0;i<nrw;i++)
	{
	  sum+=weights[i]; //should we use absolute value instead??
	}
      
      if(sum!=0)
	for(int i=0;i<nrw;i++)
	  {
	    weights[i]/=sum;
	  }
      else cdebug(3)<<"cannot make weighted average, sum of weights == 0, use weighted sum instead"<<endl;

    }
  
}


Vells WMean::evaluate (const Request& req, const LoShape& shape,
                     const vector<const Vells*>& values)
{

  NormWeights();
  return WSum::evaluate (req,shape,values);
  
}


} // namespace Meq
