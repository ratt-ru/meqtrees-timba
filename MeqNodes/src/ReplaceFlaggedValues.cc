//# ReplaceFlaggedValues.cc: Take exponent of a node
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
//# $Id: ReplaceFlaggedValues.cc 5418 2007-07-19 16:49:13Z oms $

#include <MeqNodes/ReplaceFlaggedValues.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;


namespace Meq {    


ReplaceFlaggedValues::ReplaceFlaggedValues()
: Function(-2)
{ 
  value_ = 0;
}

ReplaceFlaggedValues::~ReplaceFlaggedValues()
{}

void ReplaceFlaggedValues::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Function::setStateImpl(rec,initializing);
  rec[FValue].get(value_,initializing);
}

// evaluateFlags()
void ReplaceFlaggedValues::evaluateFlags (Vells::Ref &out,const Request &,const LoShape &,
                                          const vector<const VellSet *> &pvs)
{
  // output flags come from first child
  if( pvs[0]->hasDataFlags() )
    out.attach(pvs[0]->dataFlags());
  // flags for values marked for replacement come from second child
  flags_.detach();
  for( uint i=1; i<pvs.size(); i++ )
    if( pvs[i] && !pvs[i]->isNull() && pvs[i]->hasDataFlags() )
      Vells::mergeFlags(flags_,pvs[i]->dataFlags(),flagmask_[i]);
}


Vells ReplaceFlaggedValues::evaluate (const Request&,const LoShape & inshape,
		     const vector<const Vells*>& values)
{
  Vells val = *(values[0]);
  if( flags_ )
  {
    if( val.isReal() )
      val.replaceFlaggedValues(*flags_,creal(value_));
    else
      val.replaceFlaggedValues(*flags_,value_);
    val.clearDataFlags();
  }
  return val;
}

} // namespace Meq
