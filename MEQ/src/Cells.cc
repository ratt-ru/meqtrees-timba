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
#include <MEQ/Cells.h>
#include <DMI/DataArray.h>

namespace MEQ {

Cells::Cells (const DataRecord& rec)
: DataRecord   (rec),
  itsDomain    (new Domain(rec[AidDomain])),
  itsNfreq     (rec[AidNfreq]),
  itsTimes     (rec[AidTimes].as<LoVec_double>()),
  itsTimeSteps (rec[AidTimeSteps].as<LoVec_double>())
{
  itsFreqStep  = (itsDomain->endFreq() - itsDomain->startFreq()) / itsNfreq;
}

Cells::Cells (const Domain& domain, int nfreq, int ntimes)
: itsNfreq     (nfreq),
  itsTimes     (ntimes),
  itsTimeSteps (ntimes)
{
  Assert (ntimes > 0  &&  nfreq > 0);
  itsFreqStep = (domain.endFreq() - domain.startFreq()) / nfreq;
  double time = domain.startTime();
  double step = (domain.endTime() - time) / ntimes;
  time += step/2;
  for (int i=0; i<ntimes; i++) {
    itsTimes(i)     = time;
    itsTimeSteps(i) = step;
    time += step;
  }
  setDMI (domain);
}
 
Cells::Cells (const Domain& domain, int nfreq,
	      const LoVec_double& startTimes,
	      const LoVec_double& endTimes)
: itsNfreq     (nfreq),
  itsTimes     (startTimes.size()),
  itsTimeSteps (startTimes.size())
{
  Assert (startTimes.size() == endTimes.size());
  Assert (startTimes.size() > 0  &&  nfreq > 0);
  for (int i=0; i<startTimes.size(); i++) {
    Assert (endTimes(i) > startTimes(i));
    Assert (startTimes(i) >= domain.startTime());
    Assert (endTimes(i) <= domain.endTime());
    itsTimeSteps(i) = endTimes(i) - startTimes(i);
    itsTimes(i) = startTimes(i) + itsTimeSteps(i) / 2;
  }
  setDMI (domain);
}

Cells::~Cells()
{
  DataRecord::operator= (DataRecord());
}

std::ostream& operator<< (std::ostream& os, const MEQ::Cells& cells)
{
  os << "MEQ::Cells [" << cells.nfreq() << ','
     << cells.itsTimes.size() << "]  "
     << cells.domain() << endl;
  return os;
}


void Cells::setDMI (const Domain& domain)
{
  itsDomain = new Domain(domain);
  this->operator[](AidDomain) <<= static_cast<DataField*>(itsDomain);
  this->operator[](AidNfreq) = itsNfreq;
  this->operator[](AidTimes) = itsTimes;
  this->operator[](AidTimeSteps) = itsTimeSteps;
}

} // namespace MEQ
