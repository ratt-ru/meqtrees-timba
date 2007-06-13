//# StationBeam.h: Calculates beam gasin of a StationBeam tracking a source at Ra, Dec
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
//# $Id: StationBeam.h 5175 2007-05-15 21:21:00Z twillis $

// A MeqStationBeam node transforms Right Ascension and Declination coordinates 

#ifndef MEQNODES_STATIONBEAM_H
#define MEQNODES_STATIONBEAM_H
    
#include <MEQ/TensorFunction.h>
#include <measures/Measures/MPosition.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::StationBeam
#pragma aid RA Dec X Y Z
#pragma aid Filename Phi0

namespace Meq {    



class StationBeam : public TensorFunction
{
public:
  StationBeam();

  virtual ~StationBeam();

  virtual TypeId objectType() const
    { return TpMeqStationBeam; }

protected:
  // method required by TensorFunction
  // Returns cells of result.
  // This version just uses the time axis.
  virtual void computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request);

  // method required by TensorFunction
  // Returns shape of result.
  // Also check child results for consistency
  virtual LoShape getResultDims (const vector<const LoShape *> &input_dims);
    
  // method required by TensorFunction
  // Evaluates StationBeam for a given set of children values
  virtual void evaluateTensors (std::vector<Vells> & out,   
       const std::vector<std::vector<const Vells *> > &args );

  // Used to test if we are initializing with an observatory name
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

private:
  string coordfile_name_; //file to store coordinates
  blitz::Array<double,2> p_;//array of coordinates
  double ra_,dec_; //tracking centre 
  double x_,y_,z_;//coords of phase centre in ITRF
  double phi0_; //rotation around zenith
};



} // namespace Meq

#endif
