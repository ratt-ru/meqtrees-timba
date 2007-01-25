//# ObjectRADec.h: return the grid along an axis (generalization of Time and Freq)
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
//# $Id: ObjectRADec.h 3343 2006-04-03 16:02:29Z smirnov $

#ifndef MEQNODES_OBJECTRADEC_H
#define MEQNODES_OBJECTRADEC_H
    
#include <MEQ/Node.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::ObjectRADec
#pragma aid Obj Name

namespace Meq {    


class ObjectRADec : public Node
{
public:
  typedef enum {
    SUN=0x00001,
    JUPITER=0x0002,
  } ::BodyType;


  ObjectRADec();

  virtual ~ObjectRADec();
  
  virtual TypeId objectType() const
    { return TpMeqObjectRADec; }

protected:
  virtual void setStateImpl (DMI::Record::Ref& rec, bool initializing);

  // Evaluate the value for the given request.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

private:
  string oname_;
  BodyType type_;
};


} // namespace Meq

#endif
