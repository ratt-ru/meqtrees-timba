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

#include <Common/Debug.h>
#include <DMI/DataField.h>
#include "Domain.h"
#include "MeqVocabulary.h"

namespace Meq {

// pull in registry definitions
static int _dum = aidRegistry_Meq();
static NestableContainer::Register reg(TpMeqDomain,True);

//##ModelId=3F86886E030D
Domain::Domain()
{
  range_[FREQ][0] = range_[TIME][0] = 0;
  range_[FREQ][1] = range_[TIME][1] = 1;
}

//##ModelId=3F86886E030E
Domain::Domain (const DataRecord & rec,int flags)
: DataRecord(rec,(flags&~DMI::WRITE)|DMI::DEEP|DMI::READONLY)
{
  validateContent();
}

//##ModelId=3F95060C00A7
Domain::Domain (double startFreq, double endFreq,
		            double startTime, double endTime)
{
  AssertMsg (startFreq < endFreq, "Meq::Domain: startFreq " << startFreq <<
	     " must be < endFreq " << endFreq);
  AssertMsg (startTime < endTime, "Meq::Domain: startTime " << startTime <<
	     " must be < endTime " << endTime);
  range_[FREQ][0] = startFreq;
  range_[FREQ][1] = endFreq;
  range_[TIME][0] = startTime;
  range_[TIME][1] = endTime;
  (*this)[FFreq] <<= new DataField(Tpdouble,2,DMI::WRITE,range_[FREQ]);
  (*this)[FTime] <<= new DataField(Tpdouble,2,DMI::WRITE,range_[TIME]);
}


//##ModelId=400E5305010B
void Domain::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  try
  {
    Hook fhook(*this,FFreq);
    Hook thook(*this,FTime);
    // if neither is specified, use default
    if( !fhook.exists() && !thook.exists() )
    {
      range_[FREQ][0] = range_[TIME][0] = 0;
      range_[FREQ][1] = range_[TIME][1] = 1;
    }
    else
    {
      int size1,size2;
      const double *fq = fhook.as_p<double>(size1);
      const double *tm = thook.as_p<double>(size2);
      FailWhen(size1!=2,"bad Freq field");
      FailWhen(size2!=2,"bad Time field");
      range_[FREQ][0] = fq[0]; range_[FREQ][1] = fq[1];
      range_[TIME][0] = tm[0]; range_[TIME][1] = tm[1];
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
  return Domain(min(a.range_[FREQ][0],b.range_[FREQ][0]),max(a.range_[FREQ][1],b.range_[FREQ][1]),
                min(a.range_[TIME][0],b.range_[TIME][0]),max(a.range_[TIME][1],b.range_[TIME][1]));
}

//##ModelId=400E53050125
void Domain::show (std::ostream& os) const
{
  os << "Meq::Domain [" << start(FREQ) << ":" << end(FREQ) << ','
                        << start(TIME) << ":" << end(TIME) << "]";
}


} // namespace Meq
