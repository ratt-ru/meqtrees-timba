//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7F3B77034D.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7F3B77034D.cm

//## begin module%3C7F3B77034D.cp preserve=no
//## end module%3C7F3B77034D.cp

//## Module: Timestamp%3C7F3B77034D; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar9\oms\LOFAR\src-links\DMI\Timestamp.cc

//## begin module%3C7F3B77034D.additionalIncludes preserve=no
//## end module%3C7F3B77034D.additionalIncludes

//## begin module%3C7F3B77034D.includes preserve=yes
#include <math.h>
#include <time.h>
//## end module%3C7F3B77034D.includes

// Timestamp
#include "DMI/Timestamp.h"
//## begin module%3C7F3B77034D.declarations preserve=no
//## end module%3C7F3B77034D.declarations

//## begin module%3C7F3B77034D.additionalDeclarations preserve=yes
//## end module%3C7F3B77034D.additionalDeclarations


// Class Timestamp 

//## begin Timestamp::tsnow%3C8F68EA004C.attr preserve=no  private: static Timestamp {U} 
Timestamp Timestamp::tsnow;
//## end Timestamp::tsnow%3C8F68EA004C.attr

Timestamp::Timestamp (double sec1)
  //## begin Timestamp::Timestamp%3C95C5F90389.hasinit preserve=no
  //## end Timestamp::Timestamp%3C95C5F90389.hasinit
  //## begin Timestamp::Timestamp%3C95C5F90389.initialization preserve=yes
  //## end Timestamp::Timestamp%3C95C5F90389.initialization
{
  //## begin Timestamp::Timestamp%3C95C5F90389.body preserve=yes
  sec_ = (long) floor(sec1);
  usec_ = (long) floor((sec1-sec_)*1e+6);
  //## end Timestamp::Timestamp%3C95C5F90389.body
}



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

string Timestamp::toString (const char *format) const
{
  //## begin Timestamp::toString%3CA06AE50335.body preserve=yes
  time_t tm = sec_;
  char tmp[256];
  strftime(tmp,sizeof(tmp),format,localtime(&tm));
  return tmp;
  //## end Timestamp::toString%3CA06AE50335.body
}

Timestamp & Timestamp::operator += (const Timestamp &other)
{
  //## begin Timestamp::operator +=%3C7F3D500287.body preserve=yes
  sec_ += other.sec_;
  usec_ += other.usec_;
  normalize();
  return *this;
  //## end Timestamp::operator +=%3C7F3D500287.body
}

Timestamp & Timestamp::operator -= (const Timestamp &other)
{
  //## begin Timestamp::operator -=%3C7F3D720312.body preserve=yes
  sec_ -= other.sec_;
  usec_ -= other.usec_;
  normalize();
  return *this;
  //## end Timestamp::operator -=%3C7F3D720312.body
}

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
  //## begin Timestamp%3C7F3B1D025E.declarations preserve=yes
  //## end Timestamp%3C7F3B1D025E.declarations

//## begin module%3C7F3B77034D.epilog preserve=yes
//## end module%3C7F3B77034D.epilog


// Detached code regions:
#if 0
//## begin Timestamp::Timestamp%3C7F3B1D025E_const.body preserve=yes
  struct timeval tm;
  gettimeofday(&tm,0);
  sec_ = tm.tv_sec;
  usec_ = tm.tv_usec;
//## end Timestamp::Timestamp%3C7F3B1D025E_const.body

#endif
