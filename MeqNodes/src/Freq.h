//# Freq.h: Give the frequencies
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

#ifndef MEQ_FREQ_H
#define MEQ_FREQ_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Freq

namespace Meq {    


//##ModelId=400E530302C0
class Freq : public Node
{
public:
    //##ModelId=400E53050214
  Freq();

    //##ModelId=400E53050215
  virtual ~Freq();
  
    //##ModelId=400E53050217
  virtual void init (DataRecord::Ref::Xfer &initrec, Forest* frst);
  
    //##ModelId=400E5305021B
  virtual TypeId objectType() const
    { return TpMeqFreq; }

protected:
  // Evaluate the value for the given request.
    //##ModelId=400E5305021D
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

};


} // namespace Meq

#endif
