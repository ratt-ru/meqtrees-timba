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
  freq0_(0),freq1_(1),time0_(0),time1_(1)
{
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
  double *fld = (*this)[HIID()].as_wp<double>();
  fld[0] = freq0_ = startFreq;
  fld[1] = freq1_ = endFreq;
  fld[2] = time0_ = startTime;
  fld[3] = time1_ = endTime;
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
      freq0_ = fld[0];
      freq1_ = fld[1];
      time0_ = fld[2];
      time1_ = fld[3];
    }
    else
    {
      freq0_ = time0_ = 0;
      freq1_ = time1_ = 1;
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

Domain Domain::envelope (const Domain &a,const Domain &b)
{
  using std::min;
  using std::max;
  return Domain(min(a.freq0_,b.freq0_),max(a.freq1_,b.freq1_),
                min(a.time0_,b.time0_),max(a.time1_,b.time1_));
}

//##ModelId=400E53050125
void Domain::show (std::ostream& os) const
{
  os << "Meq::Domain [" << startFreq() << " : " << endFreq() << ','
     << startTime() << " : " << endTime() << "]";
}


} // namespace Meq
