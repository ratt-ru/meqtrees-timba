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
#include <MEQ/Result.h>

#pragma types #Meq::Function


namespace Meq {    

class Request;


class Function : public Node
{
public:
  Function();

  virtual ~Function();

  // Get the result for the given request.
  // The default implementation works as follows:
  // <ul>
  // <li> It evaluates the function for the main value and all perturbed values
  //   by calling the evaluate or evaluateVells function.
  // <li> First it calls evaluate for the main value. It that returns an
  //   empty value, it knows that evaluateVells should be called.
  // <li> Function evaluate is meant for returning the result by value.
  //   Usually this is the best way to go.
  // <li> Function evaluateVells is slightly faster to use because the
  //   result is passed in by reference, so one can, say, use
  //   result+=value. See class Add for an example of that.
  //   It requires that the result type and shape are known. They are
  //   determined by function resultTypeShape. Its default implementation is
  //   usually sufficient.
  // <li> For the calculation of all perturbed values the same function as
  //   for the main value is used.
  // <li> Usually the fastest way to go is to overload function getResultImpl
  //   in the derived class, because in that way some values can be
  //   calculated once for main value and perturbed values.
  // </ul>
  virtual int getResultImpl (ResultSet::Ref &resref, const Request&, bool newReq);

  // Find the shape of the result for evaluate. Usually the default 
  // implementation is sufficient which takes
  // the maximum of the values of the children.
  virtual LoShape resultShape (const vector<Vells*>& values);

  // Evaluate the value for the given request.
  // The default throws an exception.
  // NB: this will be phased out
  virtual void evaluateVells (Vells& result,const Request&,
			      const vector<Vells*>& values);

    
  // Evaluate the value for the given request. The output shape is
  // precomputed with resultShape() and passed in as the shape argument.
  virtual Vells evaluate (const Request &req,const LoShape &,const vector<Vells*>& values)
  { Vells res; evaluateVells(res,req,values); return res; }

  // Find all spids for this node by merging the spids in all results.
  static vector<int> findSpids (const vector<Result*>&);

  // Returns the class TypeId
  virtual TypeId objectType() const;

  // Check the children after they have been resolved in class Node.
  // The order of the children is the order as given when the Node object
  // was created.
  virtual void checkChildren();

  // Same as checkChildren, but it also tests if the number of children
  // is correct (using the function testChildren).
  // This is only done if not already done yet for this node object.
  // If already done, false is returned.
  bool convertChildren (int nchild);

  // Same as convertChildren, but the order of the children is the order as
  // the HIIDs given in the vector. If the number of children exceeds
  // the vector size, the remaining ones are stored at the end in their
  // original order.
  // If nchild==0, it is set to the vector size.
  // This is only done if not already done yet for this node object.
  // If already done, false is returned.
  bool convertChildren (const vector<HIID>& childNames, int nchild=0);

  // Test the number of children.
  // If the argument nchild is positive, it checks if the number
  // of children matches exactly. If negative, it checks if the
  // number of children is at least nchild. If zero, no test is done.
  void testChildren (int nchild) const;

  // Test if the types of the children match the given types.
  // It has to be done after check/convertChildren is done.
  void testChildren (const vector<TypeId>& childTypes) const;

protected:
  vector<Node*>& children()
    { return itsChildren; }

private:
  vector<Node*> itsChildren;
};


} // namespace Meq

#endif
