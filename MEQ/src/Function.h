//# Function.h: Base class for an expression node
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

#ifndef MEQ_FUNCTION_H
#define MEQ_FUNCTION_H
    
#include <MEQ/Node.h>
#include <MEQ/VellSet.h>

#pragma types #Meq::Function
#pragma aid Flag Mask


namespace Meq { using namespace DMI;    

class Request;

//##ModelId=3F86886E01A8
class Function : public Node
{
public:
    //##ModelId=3F86886E03C5
  Function (int nchildren=-1,const HIID *labels = 0,int nmandatory=-1);

    //##ModelId=3F86886E03D1
  virtual ~Function();

  // Returns the class TypeId
    //##ModelId=400E53070274
  virtual TypeId objectType() const;
  
  // helper func: find all spids for this node by merging the spids in all results.
    //##ModelId=3F86886F0108
  static vector<int> findSpids (int & npertsets,const vector<const VellSet*> &);

protected:
  // may be called if the Node can support missing data (see evaluate() below)
  void allowMissingData ();
    
  // Evaluate the value for the given request. The output shape is
  // passed in as the shape argument (usually taken from first child, rest
  // must conform).
  // Note that if some children return missing data (i.e. empty Result),
  // and allowMissingData() has been called, then the appropriate Vells* 
  // will be 0. 
  // Must be reimplemented, as default version throws an exception.
    //##ModelId=3F86886F00B0
  virtual Vells evaluate (const Request &req,const LoShape &shape,const vector<const Vells*>&);
  
  // Evaluate the flags for the given request, and return them in 'out'.
  // If out is not a valid ref, a new Vells should be created. (If it is,
  // assume some initial flags are passed in, and do not reinitialize).
  // The output shape is passed in as the shape argument. 
  // If no flags were generated (e.g. due to all children being flagless),
  // 'out' may be left uninitialized.
  // Note that if some children return missing data (i.e. empty Result),
  // and allowMissingData() has been called, then the appropriate VellSet* 
  // will be 0. 
  // Default version returns a bitwise-OR of all valid child flags, with
  // flagmasks applied.
    //##ModelId=3F86886F00B0
  virtual void evaluateFlags (Vells::Ref &out,const Request &req,const LoShape &shape,const vector<const VellSet *> &pvs);


  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  // Get the result for the given request.
  // The default implementation works as follows:
  // <ul>
  // <li> It evaluates the function for the main value and all perturbed values
  //   by calling the evaluate or evaluateVells function.
  // <li> First it calls evaluate for the main value. 
  // <li> For the calculation of all perturbed values the same function as
  //   for the main value is used.
  // </ul>
    //##ModelId=3F86886E03DD
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  vector<int> flagmask_;
  bool enable_flags_;

private:
    
//*** OMS 08/07/04: phased out, see above
//    //##ModelId=3F86886E03A4
//  vector<Node*> itsChildren;

  bool allow_missing_data_;
    
  bool force_integrated_;
  
  bool integrated_;
  
  int auto_resampling_;
};


template<int N>
class FunctionX : public Function
{
public:
  FunctionX() 
    : Function(N)
  {}

  virtual ~FunctionX() 
  {}
  
};

typedef FunctionX<1> Function1;
typedef FunctionX<2> Function2;

} // namespace Meq

#endif
