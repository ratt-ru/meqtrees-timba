//# Constant.h: Real or complex constant
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

#ifndef MEQNODES_CONSTANT_H
#define MEQNODES_CONSTANT_H

//# Includes
#include <MEQ/Node.h>
#include <MEQ/Vells.h>
#include <TimBase/lofar_vector.h>
#include <MeqNodes/TID-MeqNodes.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Constant

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqConstant
//  Represents a constant node. A MeqConstant cannot have any children.
//field: value 0.0  
//  value of constant - double or complex double scalar or array (if array
//  is used, a tensor will be returned)
//field: vells F  
//  variable constant (ugly hack) - expected double or complex double array.
//  Subsequent request cells must have the same shape.
//field: integrated F  
//  if true, constant represents an integration -- result value will be 
//  multiplied by cell size
//defrec end

namespace Meq {

//##ModelId=400E53030283
class Constant: public Node
{
public:
  // Create a "null" constant returning empty vellset
  Constant ();
  // Create a constant with the given value.
    //##ModelId=400E5305008F
  explicit Constant (double value,bool integrated=false);
    //##ModelId=400E53050094
  explicit Constant (const dcomplex& value,bool integrated=false);

    //##ModelId=400E53050098
  virtual ~Constant();

    //##ModelId=400E5305009A
  virtual TypeId objectType() const
    { return TpMeqConstant; }

  // Get the requested result of the constant.
    //##ModelId=400E5305009C
  virtual int getResult (Result::Ref& resref, 
                         const std::vector<Result::Ref>& childres,
                         const Request& req, bool newreq);

    //##ModelId=400E530500AD
  //## Standard debug info method
  virtual string sdebug (int detail = 1, const string& prefix = "",
			 const char* name = 0) const;

protected:
  // Set the state from the record.
    //##ModelId=400E530500B5
  virtual void setStateImpl (DMI::Record::Ref& rec, bool initializing);

private:
    //##ModelId=400E53050085
  Result::Ref result_;

  bool integrated_;
  
  bool has_shape_;
};


} // namespace Meq

#endif
