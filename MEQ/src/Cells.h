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
#pragma types #Meq::Cells

namespace Meq {

//##ModelId=3F86886E017A
class Cells : public DataRecord
{
public:
    //##ModelId=400E53030256
  typedef CountedRef<Cells> Ref;
    
    //##ModelId=3F86886E02C1
  Cells ();
  // Construct from DataRecord. 
    //##ModelId=3F86886E02C8
  Cells (const DataRecord &other,int flags=DMI::PRESERVE_RW,int depth=0);
  // construct from others
    //##ModelId=3F95060B01D3
  Cells (const Domain& domain, int nfreq, int ntimes);
    //##ModelId=400E530403A0
  Cells (const Domain& domain, int nfreq,
	       const LoVec_double& startTimes,
	       const LoVec_double& endTimes);
    //##ModelId=3F86886E02D1
  ~Cells();
  
    //##ModelId=400E530403C1
  virtual TypeId objectType () const
  { return TpMeqCells; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E530403C5
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Cells(*this,flags|(depth>0?DMI::DEEP:0)); }
  
//   // implement standard clone method via copy constructor
//   virtual CountedRefTarget* clone (int flags, int depth) const
//   { return new Cells(*this,flags,depth); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Cells object is made from a DataRecord
  // (or when the underlying DataRecord is privatized, etc.)
    //##ModelId=400E530403DB
  virtual void validateContent ();
  
  // Get domain.
    //##ModelId=3F86886E02D2
  const Domain& domain() const
  { FailWhen(!itsDomain,"no domain"); return *itsDomain; }

  // Get nr of freq.
    //##ModelId=3F86886E02D4
  int nfreq() const
    { return itsNfreq; }

  // Get nr of times.
    //##ModelId=3F86886E02D6
  int ntime() const
    { return itsTimes.size(); }

  // Get step in frequency.
    //##ModelId=3F86886E02D8
  double stepFreq() const
    { return itsFreqStep; }

  // Get the i-th time.
    //##ModelId=3F86886E02DA
  double time (int i) const
    { return itsTimes(i); }

  // Get the i-th time step.
    //##ModelId=3F86886E02E0
  double stepTime (int i) const
    { return itsTimeSteps(i); }

    //##ModelId=400E530403DE
  bool operator== (const Cells& that) const;

    //##ModelId=400E53050002
  bool operator!= (const Cells& that) const
    { return !(*this == that); }

  // print to stream
    //##ModelId=400E5305000E
  void show (std::ostream&) const;
  
private:
  // Setup DataRecord with domain; sets up new arrays with given sizes
    //##ModelId=400E53050019
  void setDataRecord (const Domain&,int nfreq,int ntimes);

    //##ModelId=3F86BFF80150
  const Domain* itsDomain;
    //##ModelId=3F86886E02AC
  double        itsFreqStep;
    //##ModelId=3F86886E02B1
  int           itsNfreq;
    //##ModelId=3F86886E02B6
  LoVec_double  itsTimes;
    //##ModelId=3F86886E02BC
  LoVec_double  itsTimeSteps;
};

} //namespace Meq

inline std::ostream& operator << (std::ostream& os, const Meq::Cells& cells)
{
  cells.show(os);
  return os;
}


#endif
