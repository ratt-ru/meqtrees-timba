//# Domain.h: The domain for an expression
//#
//# Copyright (C) 2002
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

#ifndef MEQ_DOMAIN_H
#define MEQ_DOMAIN_H


// This class represents a domain for which an expression has to be
// evaluated.
// The domain is normalized to the interval [-1,1].
//    offset = (st+end)/2    and    scale = (end-st)/2.
//    st = off-scale         and    end = off+scale
// Then
//    scaledvalue = (realvalue - offset) / scale


#include <DMI/DataField.h>
#include <MEQ/TID-Meq.h>

#pragma types #Meq::Domain

namespace Meq {


//##ModelId=3F86886E0183
class Domain : public DataField
{
public:
  // Create a time,frequency default domain of -1:1,-1:1..
    //##ModelId=3F86886E030D
  Domain();

  // Create from an existing data field.
    //##ModelId=3F86886E030E
  Domain (const DataField&,int flags=DMI::PRESERVE_RW);

  // Create a time,frequency domain.
    //##ModelId=3F95060C00A7
  Domain (double startFreq, double endFreq,
	  double startTime, double endTime);

    //##ModelId=400E530500F5
  virtual TypeId objectType () const
  { return TpMeqDomain; }
  
  // implement standard clone method via copy constructor
    //##ModelId=400E530500F9
  virtual CountedRefTarget* clone (int flags, int depth) const
  { return new Domain(*this,flags|(depth>0?DMI::DEEP:0)); }
  
  // validate record contents and setup shortcuts to them. This is called 
  // automatically whenever a Domain is made from a DataField
  // (or when the underlying DataField is privatized, etc.)
    //##ModelId=400E5305010B
  virtual void validateContent ();
  
  // Get offset and scale value.
    //##ModelId=3F86886E0316
  double offsetFreq() const
    { return itsOffsetFreq; }
    //##ModelId=3F86886E0318
  double scaleFreq() const
    { return itsScaleFreq; }
    //##ModelId=3F86886E031A
  double offsetTime() const
    { return itsOffsetTime; }
    //##ModelId=3F86886E031C
  double scaleTime() const
    { return itsScaleTime; }

  // Transform a value to its normalized value.
    //##ModelId=3F86886E031F
  double normalizeFreq (double value) const
    { return (value - itsOffsetFreq) / itsScaleFreq; }
    //##ModelId=3F86886E0324
  double normalizeTime (double value) const
    { return (value - itsOffsetTime) / itsScaleTime; }

  // Get the start, end, and step of the domain.
    //##ModelId=3F86886E032C
  double startFreq() const
    { return itsOffsetFreq - itsScaleFreq; }
    //##ModelId=3F86886E032E
  double endFreq() const
    { return itsOffsetFreq + itsScaleFreq; }
    //##ModelId=3F86886E0330
  double startTime() const
    { return itsOffsetTime - itsScaleTime; }
    //##ModelId=3F86886E0332
  double endTime() const
    { return itsOffsetTime + itsScaleTime; }

    //##ModelId=400E5305010E
  bool operator== (const Domain& that) const
  { return itsOffsetFreq == that.itsOffsetFreq
       &&  itsScaleFreq  == that.itsScaleFreq
       &&  itsOffsetTime == that.itsOffsetTime
       &&  itsScaleTime  == that.itsScaleTime; }
  
  bool subsetOf (const Domain &other) const
  { return 
      startFreq() >= other.startFreq() && endFreq() <= other.endFreq() &&
      startTime() >= other.startTime() && endTime() <= other.endTime(); }
  
  bool supersetOf (const Domain &other) const
  { return other.subsetOf(*this); }
  

    //##ModelId=400E5305011A
  bool operator!= (const Domain& that) const
    { return !(*this == that); }
  
  // print to stream
    //##ModelId=400E53050125
  void show (std::ostream&) const;

private:
    //##ModelId=3F86886E02F8
  double itsOffsetFreq;
    //##ModelId=3F86886E02FD
  double itsScaleFreq;
    //##ModelId=3F86886E0302
  double itsOffsetTime;
    //##ModelId=3F86886E0307
  double itsScaleTime;
};

} // namespace Meq

inline std::ostream& operator << (std::ostream& os, const Meq::Domain& dom)
{
  dom.show(os);
  return os;
}

#endif
