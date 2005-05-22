//# AzEl.h: Calculate AzEl of a source from J2000 Ra, Dec
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

// A MeqAzEl node transforms Right Ascension and Declination coordinates 
// (first and second children) into observed Azimuth and Elevation. 
// Since azimuth and elevation are dependent on the location on the Earth 
// where a source is observed, you must provide this mode with a location. 
// This can be done in two ways. If you instantiate the node with the name 
// of an observatory known to aips++, then the location of the observatory, 
// in ITRF coordinates, is used for the transformation. If you do not supply 
// the node with an observatory name, then you must supply the 
// ITRF X,Y,Z cooordinates of the station location (with third, fourth 
// and fifth children).

// A MeqAzEl node can be set up by specifying the following field in its 
// init-record: 

// field 	 description
// observatory 	name of observatory

// The name of the observatory can presently be any one of 
// ALMA ARECIBO ATCA BIMA CLRO DRAO DWL GB GBT GMRT IRAM PDB 
// IRAM_PDB JCMT MOPRA MOST NRAO12M NRAO_GBT PKS VLA VLBA WSRT.

#ifndef MEQNODES_AZEL_H
#define MEQNODES_AZEL_H
    
#include <MEQ/Function.h>
#include <measures/Measures/MPosition.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::AzEl
#pragma aid RA Dec 
#pragma aid Observatory

namespace Meq {    

class AzEl : public Function
{
public:

  AzEl(const string& name);
  AzEl();

  virtual ~AzEl();

  virtual TypeId objectType() const
    { return TpMeqAzEl; }
  
  LocalDebugContext;

protected:
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  // Get the result for the given request.
  virtual int getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq);
private:
  string obs_name_;

};


} // namespace Meq

#endif
