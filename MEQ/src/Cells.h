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
#include <MEQ/AID-Meq.h>
#include <DMI/DataRecord.h>
#include <Common/Lorrays.h>
#include <ostream>

#pragma aidgroup Meq
#pragma aid Domain Nfreq Times TimeSteps
#pragma types #Meq::Cells

namespace Meq {

class Cells : public DataRecord
{
public:
  typedef CountedRef<Cells> Ref;
    
  Cells ();
  // Construct from DataRecord. 
  Cells (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  // construct from others
  Cells (const Domain& domain, int nfreq, int ntimes);
  Cells (const Domain& domain, int nfreq,
	       const LoVec_double& startTimes,
	       const LoVec_double& endTimes);
  ~Cells();
  
  virtual TypeId objectType () const
  { return TpMeqCells; }
  
//   // implement standard clone method via copy constructor
//   virtual CountedRefTarget* clone (int flags, int depth) const
//   { return new Cells(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Cells object is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
  virtual void validateContent ();
  
  // Get domain.
  const Domain& domain() const
  { FailWhen(!itsDomain,"no domain"); return *itsDomain; }

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

  friend std::ostream& operator<< (std::ostream& os, const Meq::Cells& cells);

private:
  // Setup DataRecord with domain; sets up new arrays with given sizes
  void setDataRecord (const Domain&,int nfreq,int ntimes);

  const Domain* itsDomain;
  double        itsFreqStep;
  int           itsNfreq;
  LoVec_double  itsTimes;
  LoVec_double  itsTimeSteps;
};

} //namespace Meq

#endif
