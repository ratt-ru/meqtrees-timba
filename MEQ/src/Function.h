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

namespace MEQ {    

class Request;


class Function : public Node
{
public:
  Function();

  virtual ~Function();

  // Get the result for the given request.
  // By default it calls evaluate.
  virtual int getResult (Result::Ref &resref, const Request&);

  // Find the type and shape of the result for evaluate.
  // It returns true if the result is real; otherwise false.
  // It is used when evaluate is used.
  // Usually the default implementation is sufficient.
  virtual bool resultTypeShape (int& nx, int& ny, const Request&,
				const vector<Vells*>& values);

  // Evaluate the value for the given request.
  virtual void evaluate (Vells& result, const Request&,
			 const vector<Vells*>& values);

  // Find all spids for this node by merging the children's spids.
  vector<int> findSpids (const vector<Result::Ref>&) const;

  virtual void init (DataRecord::Ref::Xfer& initrec);

  virtual void setState (const DataRecord& rec);
    
    
  //## Standard debug info method
  virtual string sdebug (int detail = 1, const string& prefix = "",
			 const char* name = 0) const;

protected:
  vector<Function*>& children()
    { return itsChildren; }

private:
  vector<Function*> itsChildren;
};


} // namespace MEQ

#endif
