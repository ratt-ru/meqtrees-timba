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


namespace MEQ {


class Domain : public DataField
{
public:
  // Create a time,frequency default domain of -1:1,-1:1..
  Domain();

  // Create from an existing data field.
  Domain (const DataField&);

  // Create a time,frequency domain.
  Domain (double startFreq, double endFreq,
	  double startTime, double endTime);

  // Get offset and scale value.
  double offsetFreq() const
    { return itsOffsetFreq; }
  double scaleFreq() const
    { return itsScaleFreq; }
  double offsetTime() const
    { return itsOffsetTime; }
  double scaleTime() const
    { return itsScaleTime; }

  // Transform a value to its normalized value.
  double normalizeFreq (double value) const
    { return (value - itsOffsetFreq) / itsScaleFreq; }
  double normalizeTime (double value) const
    { return (value - itsOffsetTime) / itsScaleTime; }

  // Get the start, end, and step of the domain.
  double startFreq() const
    { return itsOffsetFreq - itsScaleFreq; }
  double endFreq() const
    { return itsOffsetFreq + itsScaleFreq; }
  double startTime() const
    { return itsOffsetTime - itsScaleTime; }
  double endTime() const
    { return itsOffsetTime + itsScaleTime; }

  bool operator== (const Domain& that) const
  { return itsOffsetFreq == that.itsOffsetFreq
       &&  itsScaleFreq  == that.itsScaleFreq
       &&  itsOffsetTime == that.itsOffsetTime
       &&  itsScaleTime  == that.itsScaleTime; }

  bool operator!= (const Domain& that) const
    { return !(*this == that); }

private:
  // Set the values in the DMI DataField.
  void setDMI();

  double itsOffsetFreq;
  double itsScaleFreq;
  double itsOffsetTime;
  double itsScaleTime;
};


} // namespace MEQ

#endif
