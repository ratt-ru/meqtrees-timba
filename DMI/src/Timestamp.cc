//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "Timestamp.h"
#include <math.h>
#include <time.h>
    
namespace DMI
{

Timestamp Timestamp::tsnow;

Timestamp::Timestamp (double sec1)
{
  //## begin Timestamp::Timestamp%3C95C5F90389.body preserve=yes
  sec_ = (long) floor(sec1);
  usec_ = (long) floor((sec1-sec_)*1e+6);
  //## end Timestamp::Timestamp%3C95C5F90389.body
}

//##ModelId=3C8F67DD00BD
//## Other Operations (implementation)
const Timestamp & Timestamp::now (Timestamp *pts)
{
  //## begin Timestamp::now%3C8F67DD00BD.body preserve=yes
  static struct timeval tm;
  gettimeofday(&tm,0);
  pts->sec_ = tm.tv_sec;
  pts->usec_ = tm.tv_usec;
  return *pts;
  //## end Timestamp::now%3C8F67DD00BD.body
}

//##ModelId=3CA06AE50335
string Timestamp::toString (const char *format) const
{
  //## begin Timestamp::toString%3CA06AE50335.body preserve=yes
  char tmp[256];
  if( !strcmp(format,"ms") )
    return Debug::ssprintf("%.3f",sec_*1e+3+usec_*1e-3);
  else if( !strcmp(format,"s") )
    return Debug::ssprintf("%.6f",sec_*1e+3+usec_*1e-3);
  else if( !strcmp(format,"us") )
    return Debug::ssprintf("%ld",sec_*1000000+usec_);
  else if( !strcmp(format,"ns") )
    return Debug::ssprintf("%ld",sec_*1000000000+usec_*1000);
  else
  {
    time_t tm = sec_;
    strftime(tmp,sizeof(tmp),format,localtime(&tm));
  }
  return tmp;
  //## end Timestamp::toString%3CA06AE50335.body
}

//##ModelId=3C7F3D500287
Timestamp & Timestamp::operator += (const Timestamp &other)
{
  //## begin Timestamp::operator +=%3C7F3D500287.body preserve=yes
  sec_ += other.sec_;
  usec_ += other.usec_;
  normalize();
  return *this;
  //## end Timestamp::operator +=%3C7F3D500287.body
}

//##ModelId=3C7F3D720312
Timestamp & Timestamp::operator -= (const Timestamp &other)
{
  //## begin Timestamp::operator -=%3C7F3D720312.body preserve=yes
  sec_ -= other.sec_;
  usec_ -= other.usec_;
  normalize();
  return *this;
  //## end Timestamp::operator -=%3C7F3D720312.body
}

//##ModelId=3C7F3E68035C
void Timestamp::normalize ()
{
  //## begin Timestamp::normalize%3C7F3E68035C.body preserve=yes
  while( usec_ >= 1000000 ) 
  {
    sec_++;
    usec_ -= 1000000;
  }
  while( usec_ < 0 ) 
  {
    sec_--;
    usec_ += 1000000;
  }
  //## end Timestamp::normalize%3C7F3E68035C.body
}

// Additional Declarations
//##ModelId=3DB934F50260
  //## begin Timestamp%3C7F3B1D025E.declarations preserve=yes
Timestamp & Timestamp::operator *= (double x)
{
  double s1 = sec_ * x;
  sec_ = (long)floor(s1);
  usec_ = (long)round(usec_ * x + (s1 - sec_)*1000000);
  normalize();
  return *this;
}

string Timestamp::toString (Timestamp::TimeUnits units,int prec) const
{
  //## begin Timestamp::toString%3CA06AE50335.body preserve=yes
  int pr;
  switch( units )
  {
    case SEC:
      pr = prec<0 ? 6 : prec;
      return Debug::ssprintf("%.*f",pr,sec_+usec_*1e-6);
        
    case MSEC:
      pr = prec<0 ? 3 : prec;
      return Debug::ssprintf("%.*f",pr,sec_*1e+3+usec_*1e-3);
        
    case USEC:
      return Debug::ssprintf("%ld",sec_*1000000+usec_);
        
    case NSEC:
      return Debug::ssprintf("%ld",sec_*1000000000+usec_*1000);
  }
  return "";
}

};
