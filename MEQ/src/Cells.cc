//# Cells.cc: The cells in a given domain.
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


//# Includes
#include "Cells.h"
#include "MeqVocabulary.h"
#include <DMI/DataArray.h>

namespace Meq {

static NestableContainer::Register reg(TpMeqCells,True);

//##ModelId=3F86886E02C1
Cells::Cells ()
: itsDomain(0),itsNfreq(0)
{
}

//##ModelId=3F86886E02C8
Cells::Cells (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth)
{
  validateContent();
}

//##ModelId=3F95060B01D3
Cells::Cells (const Domain& domain, int nfreq, int ntimes)
: itsNfreq     (nfreq)
{
  setDataRecord(domain,nfreq,ntimes);
  // setup other vaklues
  itsFreqStep = (domain.endFreq() - domain.startFreq()) / nfreq;
  double time = domain.startTime();
  double step = (domain.endTime() - time) / ntimes;
  time += step/2;
  for (int i=0; i<ntimes; i++) {
    itsTimes(i)     = time;
    itsTimeSteps(i) = step;
    time += step;
  }
}

//##ModelId=400E530403A0
Cells::Cells (const Domain& domain, int nfreq,
	      const LoVec_double& startTimes,
	      const LoVec_double& endTimes)
: itsNfreq     (nfreq)
{
  int ntimes = startTimes.size();
  Assert (startTimes.size() == endTimes.size());
  Assert (startTimes.size() > 0  &&  nfreq > 0);
  setDataRecord(domain,nfreq,ntimes);
  itsFreqStep = (domain.endFreq() - domain.startFreq()) / nfreq;
  // set other values
  for (int i=0; i<startTimes.size(); i++) {
    Assert (endTimes(i) > startTimes(i));
    Assert (startTimes(i) >= domain.startTime());
    Assert (endTimes(i) <= domain.endTime());
    itsTimeSteps(i) = endTimes(i) - startTimes(i);
    itsTimes(i) = startTimes(i) + itsTimeSteps(i) / 2;
  }
}

//##ModelId=400E530403DB
void Cells::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  try
  {
    if( (*this)[FTimes].exists() )
      itsTimes.reference((*this)[FTimes].as<LoVec_double>());
    else
      itsTimes.resize(0);
    if( (*this)[FTimeSteps].exists() )
      itsTimeSteps.reference((*this)[FTimeSteps].as<LoVec_double>());
    else
      itsTimeSteps.resize(0);
    itsNfreq = (*this)[FNumFreq].as<int>(0);
    if( (*this)[FDomain].exists() )
    {
      itsDomain = (*this)[FDomain].as_p<Domain>();
      itsFreqStep  = (itsDomain->endFreq() - itsDomain->startFreq()) / itsNfreq;
    }
    else
    {
      itsDomain = 0;
      itsFreqStep = 0;
    }
    FailWhen( itsTimes.size() != itsTimeSteps.size(),"time/timestep size mismatch");
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Cells record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Cells record failed with unknown exception");
  }  
}
 
//##ModelId=3F86886E02D1
Cells::~Cells()
{
}

//##ModelId=400E530403DE
bool Cells::operator== (const Cells& that) const
{
  if (*itsDomain != *(that.itsDomain)
  ||  itsNfreq != that.itsNfreq
  ||  itsTimes.size() != that.itsTimes.size()) {
    return false;
  }
  for (int i=0; i<itsTimes.size(); i++) {
    if (itsTimes(i) != that.itsTimes(i)
    ||  itsTimeSteps(i) != that.itsTimeSteps(i)) {
      return false;
    }
  }
  return true;
}

//##ModelId=400E5305000E
void Cells::show (std::ostream& os) const
{
  os << "Meq::Cells [" << nfreq() << ','
     << itsTimes.size() << "]  "
     << domain() << endl;
}

//##ModelId=400E53050019
void Cells::setDataRecord (const Domain& domain,int nfreq,int ntimes)
{
  Assert (ntimes > 0  &&  nfreq > 0);
  (*this)[FDomain] <<= itsDomain = new Domain(domain);
  (*this)[FNumFreq] = itsNfreq = nfreq;
  (*this)[FTimes] <<= new DataArray(Tpdouble,LoShape(ntimes));
  itsTimes.reference((*this)[FTimes].as<LoVec_double>());
  (*this)[FTimeSteps] <<= new DataArray(Tpdouble,LoShape(ntimes));
  itsTimeSteps.reference((*this)[FTimeSteps].as<LoVec_double>());
}

} // namespace Meq
