//# UVBrick.h: Parameter with polynomial coefficients
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

#ifndef MEQNODES_UVBRICK_H
#define MEQNODES_UVBRICK_H

//# Includes
#include <MEQ/Node.h>
#include <images/Images/PagedImage.h>
//#include <MeqNodes/ReductionFunction.h>


#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::UVBrick

namespace Meq {


class UVBrick: public Node
	       //class UVBrick: public ReductionFunction
{
public:
  // The default constructor.
  // The object should be filled by the init method.
  UVBrick();

  virtual ~UVBrick();

  virtual TypeId objectType() const
  { return TpMeqUVBrick; }

  // Get the requested result of the Node.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);

  
 protected:

  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

 private:
  
  // It seems these images can only be global as pointers, since no default (or convenient) contructor is available for use in the UVBrick constructor.
  // Maybe use TempImage object instead of PagedImage object.
  casa::PagedImage<float>* _uvreal;
  casa::PagedImage<float>* _uvimag;
  casa::PagedImage<float>* _uvabs;
  casa::PagedImage<float>* _patch;

  double _umax;
  double _vmax;
  double _wmax;

  bool _image_exists;

  bool checkValidity(const Cells &fcells);

  void makeUVImage(const Cells &fcells, const std::vector<Result::Ref> &fchildres);

  void fillVells(Vells &fvells1, Vells &fvells2, Vells &fvells3, Vells &fvells4, const Cells &fcells);
   
};


} // namespace Meq

#endif
