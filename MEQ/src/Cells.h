//# Cells.h: The cells in a given domain.
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

#ifndef MEQ_CELLS_H
#define MEQ_CELLS_H


//# Includes
#include <MEQ/Domain.h>
#include <MEQ/AID-MEQ.h>
#include <DMI/DataRecord.h>
#include <Common/Lorrays.h>
#include <ostream>

#pragma aidgroup MEQ
#pragma aid Domain Nfreq Times TimeSteps


namespace MEQ {

class Cells : public DataRecord
{
public:
  Cells (const DataRecord&);
  Cells (const Domain& domain, int nfreq, int ntimes);
  Cells (const Domain& domain, int nfreq,
	 const LoVec_double& startTimes,
	 const LoVec_double& endTimes);

  ~Cells();

  // Get domain.
  const Domain& domain() const
    { return *itsDomain; }

  // Get nr of freq.
  int nfreq() const
    { return itsNfreq; }

  // Get nr of times.
  int ntime() const
    { return itsTimes.size(); }

  // Get step in frequency.
  double stepFreq() const
    { return itsFreqStep; }

  // Get the i-th time.
  double time (int i) const
    { return itsTimes(i); }

  // Get the i-th time step.
  double stepTime (int i) const
    { return itsTimeSteps(i); }

  bool operator== (const Cells& that) const;

  bool operator!= (const Cells& that) const
    { return !(*this == that); }

  friend std::ostream& operator<< (std::ostream& os, const MEQ::Cells& cells);

private:
  // Set the values in the DMI DataField.
  void setDMI (const Domain&);

  Domain*      itsDomain;
  double       itsFreqStep;
  int          itsNfreq;
  LoVec_double itsTimes;
  LoVec_double itsTimeSteps;
};

} //namespace MEQ

#endif
