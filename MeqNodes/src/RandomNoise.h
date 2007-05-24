//# RandomNoise.h: Give Random values
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

#ifndef MEQNODES_RANDOMNOISE_H
#define MEQNODES_RANDOMNOISE_H

//#include <MEQ/Node.h>
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::RandomNoise
#pragma aid Seed

namespace Meq {    


//##ModelId=400E530400AB
class RandomNoise : public Node
{
public:
    //##ModelId=400E535502AC
  RandomNoise();
    //##ModelId=400E535502AD
  virtual ~RandomNoise();
  
    //##ModelId=400E535502AF
  //  virtual void init (DMI::Record::Ref::Xfer &initrec, Forest* frst);
  
    //##ModelId=400E535502B3
  virtual TypeId objectType() const
  { return TpMeqRandomNoise; }

protected:
  // sets up state from state record
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  // Evaluate the value for the given request.
    //##ModelId=400E535502B5
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
};

} // namespace Meq

#endif
