//# FITSImage.cc: Read a FITS file and convert the Image HDU to  Vellsets
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

#ifndef MEQNODES_FITSIMAGE_H
#define MEQNODES_FITSIMAGE_H
    
#include <MEQ/Node.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::FITSImage
#pragma aid Filename Cutoff Mode Fraction

// The comments below are used to automatically generate a default
// init-record for the class 

//defrec begin MeqFITSImage
// Handle 4D image (FITS) files.
//field: filename ''
// FITS File Name
//field: cutoff 0.1
//  Tolerance for cutoff 
//field: mode (1 or 2)
//  mode=1 : default, returns a sixpack
//  mode=2 : returns the data as a cube, no axis mapping done
//defrec end

namespace Meq {    

class FITSImage : public Node
{
public:
  FITSImage();

  virtual ~FITSImage();

	virtual TypeId objectType() const
	{ return TpMeqFITSImage; }


protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
  
private:


	string filename_;
	double cutoff_;
	//for caching the old result
	bool has_prev_result_;
        int mode_;
	Result::Ref old_res_;
};

} // namespace Meq

#endif
