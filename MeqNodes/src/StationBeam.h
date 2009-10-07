//# StationBeam.h: Calculates beam gasin of a StationBeam tracking a source at Ra, Dec
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
//# $Id: StationBeam.h 5175 2007-05-15 21:21:00Z twillis $

// A MeqStationBeam node transforms Right Ascension and Declination coordinates 

#ifndef MEQNODES_STATIONBEAM_H
#define MEQNODES_STATIONBEAM_H
    
#include <MEQ/TensorFunction.h>
#include <measures/Measures/MPosition.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::StationBeam
#pragma aid RA Dec XYZ
#pragma aid Filename Phi0 Ref Freq Coupling

/*
 RA=RA of phase centre
 Dec=Dec of phase centre
 X,Y,Z=ITRF coords of array centre
 filename=text file with element coordinates, using array centre as origin. First row should give number of elements. The next rows should have 6 columns each.
 columns 1,2,3: x,y,z coords of X elements
 columns 4,5,6: x,y,z, coords of Y elements
 e.g.
 48
 0.1 0.2 0 0.1 0.21 0
 0.3 -0.3 0 0.3 -0.3 0
 ..
 
 phi0: rotation of coordinates around the zenith
 ref_freq: reference freq of narrowband beamformer
 coupling=text file with mutual coupling matrix
*/
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
  double phi0_;              // station layout orientation w.r.t. meridian

  string coordfile_name_; //file to store coordinates
  string couplingfile_name_; //file for mutual coupling
  blitz::Array<double,2> p_;//array of coordinates
  blitz::Array<dcomplex,2> c_;//mutual coupling matrix
  int coupling_defined_;
  Vells vfreq_;
  // all the AIPS++ things are done here
  void precompute_azel(const blitz::Array<double,1> time, blitz::Array<double,1> azval0, blitz::Array<double,1> elval0, double ra, double dec, double x, double y, double z);
};



} // namespace Meq

#endif
