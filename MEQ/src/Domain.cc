//# Domain.cc: The domain for an expression
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

#include <MEQ/Domain.h>
#include <Common/Debug.h>

namespace MEQ {

Domain::Domain()
: itsOffsetFreq (0),
  itsScaleFreq  (1),
  itsOffsetTime (0),
  itsScaleTime  (1)
{
  setDMI();
}

Domain::Domain (double startFreq, double endFreq,
		double startTime, double endTime)
{
  AssertMsg (startFreq < endFreq, "MEQ::Domain: startFreq " << startFreq <<
	     " must be < endFreq " << endFreq);
  AssertMsg (startTime < endTime, "MEQ::Domain: startTime " << startTime <<
	     " must be < endTime " << endTime);
  itsOffsetFreq = (endFreq + startFreq) * .5;
  itsScaleFreq  = (endFreq - startFreq) * .5;
  itsOffsetTime = (endTime + startTime) * .5;
  itsScaleTime  = (endTime - startTime) * .5;
  setDMI();
}


void Domain::setDMI()
{
  // Set array in DataField of 4 doubles.
  init (Tpdouble, 4);
  this->operator[](0) = startFreq();
  this->operator[](1) = endFreq();
  this->operator[](2) = startTime();
  this->operator[](3) = endTime();
}

} // namespace MEQ
