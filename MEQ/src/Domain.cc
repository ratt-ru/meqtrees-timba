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

namespace Meq {

// pull in registry definitions
static int _dum = aidRegistry_Meq();
static NestableContainer::Register reg(TpMeqDomain,True);

//##ModelId=3F86886E030D
Domain::Domain()
: // DataField(Tpdouble,4),
  itsOffsetFreq (0),
  itsScaleFreq  (1),
  itsOffsetTime (0),
  itsScaleTime  (1)
{
//  setDMI();
}

//##ModelId=3F86886E030E
Domain::Domain (const DataField& fld,int flags)
: DataField(fld,(flags&~DMI::WRITE)|DMI::DEEP|DMI::READONLY)
{
  validateContent();
}

//##ModelId=3F95060C00A7
Domain::Domain (double startFreq, double endFreq,
		double startTime, double endTime)
: DataField(Tpdouble,4)
{
  AssertMsg (startFreq < endFreq, "Meq::Domain: startFreq " << startFreq <<
	     " must be < endFreq " << endFreq);
  AssertMsg (startTime < endTime, "Meq::Domain: startTime " << startTime <<
	     " must be < endTime " << endTime);
  itsOffsetFreq = (endFreq + startFreq) * .5;
  itsScaleFreq  = (endFreq - startFreq) * .5;
  itsOffsetTime = (endTime + startTime) * .5;
  itsScaleTime  = (endTime - startTime) * .5;
  setDMI();
}

//##ModelId=400E5305010B
void Domain::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  try
  {
    if( DataField::valid() )
    {
      int size;
      const double *fld = (*this)[HIID()].as_p<double>(size);
      FailWhen(size!=4,"bad Domain field size");
      itsOffsetFreq = ( fld[1] + fld[0] ) * .5;
      itsScaleFreq  = ( fld[1] - fld[0] ) * .5;
      itsOffsetTime = ( fld[3] + fld[2] ) * .5;
      itsScaleTime  = ( fld[3] - fld[2] ) * .5;
    }
    else
    {
      itsOffsetFreq = 0;
      itsScaleFreq  = 1;
      itsOffsetTime = 0;
      itsScaleTime  = 1;
    }
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Domain field failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Domain field failed with unknown exception");
  }  
}

//##ModelId=400E53050125
void Domain::show (std::ostream& os) const
{
  os << "Meq::Domain [" << startFreq() << " : " << endFreq() << ','
     << startTime() << " : " << endTime() << "]";
}



//##ModelId=3F86886E0334
void Domain::setDMI()
{
  // Set array in DataField of 4 doubles.
  this->operator[](0) = startFreq();
  this->operator[](1) = endFreq();
  this->operator[](2) = startTime();
  this->operator[](3) = endTime();
  DataField::setWritable(False);
}

} // namespace Meq
