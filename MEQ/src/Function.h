//# Function.h: Base class for an expression node
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

#ifndef MEQ_FUNCTION_H
#define MEQ_FUNCTION_H
    
#include <MEQ/Node.h>
#include <MEQ/VellSet.h>

#pragma types #Meq::Function
#pragma aid Flag Mask


namespace Meq {    

class Request;

//##ModelId=3F86886E01A8
class Function : public Node
{
public:
    //##ModelId=3F86886E03C5
  Function (int nchildren=-1,const HIID *labels = 0,int nmandatory=0);

    //##ModelId=3F86886E03D1
  virtual ~Function();

// 11/07/04 OMS: phased out: no need, shape obtained from Cells and
// all children must conform
//   // Find the shape of the result for evaluate. Usually the default 
//   // implementation is sufficient which takes
//   // the maximum of the values of the children.
//     //##ModelId=400E5306027C
//   virtual LoShape resultShape (const vector<const Vells*>& values);

// phased out 22/03/04
//   // Evaluate the value for the given request.
//   // The default throws an exception.
//   // NB: this will be phased out
//     //##ModelId=3F95060C0321
//   virtual void evaluateVells (Vells& result,const Request&,
// 			      const vector<const Vells*>& values);

    
  // Evaluate the value for the given request. The output shape is
  // passed in as the shape argument (usually taken from first child, rest
  // mus conform)
    //##ModelId=3F86886F00B0
  virtual Vells evaluate (const Request &req,const LoShape &shape,const vector<const Vells*>&);

  // Find all spids for this node by merging the spids in all results.
    //##ModelId=3F86886F0108
  static vector<int> findSpids (const vector<const VellSet*>&);

  // Returns the class TypeId
    //##ModelId=400E53070274
  virtual TypeId objectType() const;

// /*** OMS 08/07/04:
//      phasing this out. No need to test for number of children, since
//      we can already do this by using nchildren in the constructor,
//      and testing the child types violates the whole principle of
//      "no knowledge of child types"
//      
//   // Check the children after they have been resolved in class Node.
//   // The order of the children is the order as given when the Node object
//   // was created.
//     //##ModelId=3F95060D0060
//   virtual void checkChildren();
// 
//   // Same as checkChildren, but it also tests if the number of children
//   // is correct (using the function testChildren).
//   // This is only done if not already done yet for this node object.
//   // If already done, false is returned.
//     //##ModelId=400E530702E6
//   bool convertChildren (int nchild);
// 
//   // Same as convertChildren, but the order of the children is the order as
//   // the HIIDs given in the vector. If the number of children exceeds
//   // the vector size, the remaining ones are stored at the end in their
//   // original order.
//   // If nchild==0, it is set to the vector size.
//   // This is only done if not already done yet for this node object.
//   // If already done, false is returned.
//     //##ModelId=400E5308008E
//   bool convertChildren (const vector<HIID>& childNames, int nchild=0);
// 
//   // Test the number of children.
//   // If the argument nchild is positive, it checks if the number
//   // of children matches exactly. If negative, it checks if the
//   // number of children is at least nchild. If zero, no test is done.
//     //##ModelId=400E53080325
//   void testChildren (int nchild) const;
// 
//   // Test if the types of the children match the given types.
//   // It has to be done after check/convertChildren is done.
//     //##ModelId=400E530900C1
//   void testChildren (const vector<TypeId>& childTypes) const;
// ***/

protected:
  virtual void setStateImpl (DataRecord &rec,bool initializing);

  // Get the result for the given request.
  // The default implementation works as follows:
  // <ul>
  // <li> It evaluates the function for the main value and all perturbed values
  //   by calling the evaluate or evaluateVells function.
  // <li> First it calls evaluate for the main value. 
  // <li> For the calculation of all perturbed values the same function as
  //   for the main value is used.
  // <li> Usually the fastest way to go is to overload function getResult
  //   in the derived class, because in that way some values can be
  //   calculated once for main value and perturbed values.
  // </ul>
    //##ModelId=3F86886E03DD
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

//*** OMS 08/07/04: phased out, see above
//    //##ModelId=3F86886F01D9
//  vector<Node*>& children()
//    { return itsChildren; }

  vector<int> flagmask_;
  bool enable_flags_;

private:
    
//*** OMS 08/07/04: phased out, see above
//    //##ModelId=3F86886E03A4
//  vector<Node*> itsChildren;

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
