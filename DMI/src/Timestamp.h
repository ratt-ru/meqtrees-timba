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

#ifndef DMI_Timestamp_h
#define DMI_Timestamp_h 1

#include <DMI/DMI.h>
#include <sys/time.h>

#pragma types :DMI::Timestamp

namespace DMI
{

//##ModelId=3C7F3B1D025E
class Timestamp 
{
 ImportDebugContext(DebugDMI);
 public:
    //##ModelId=3DB9343E0244
      typedef enum { SEC=0,MSEC,USEC,NSEC } TimeUnits;

  public:
    //##ModelId=3C7F3B580321
      Timestamp();

      //##ModelId=3C95C5F90389
      explicit Timestamp (long sec1, long usec1 = 0);

      //##ModelId=3DB934EA01A3
      Timestamp (double sec1);

    //##ModelId=3DB934EA0370
      bool operator==(const Timestamp &right) const;

    //##ModelId=3DB934EB0259
      bool operator!=(const Timestamp &right) const;

    //##ModelId=3DB934EC0142
      bool operator<(const Timestamp &right) const;

    //##ModelId=3DB934ED007B
      bool operator>(const Timestamp &right) const;

    //##ModelId=3DB934EE004C
      bool operator<=(const Timestamp &right) const;

    //##ModelId=3DB934EE03B3
      bool operator>=(const Timestamp &right) const;


      //##ModelId=3C8F67DD00BD
      static const Timestamp & now (Timestamp *pts = &Timestamp::tsnow);

      //##ModelId=3D1C34DB0237
      static Timestamp delta (const Timestamp &start);

      //##ModelId=3CA06AE50335
      string toString (const char *format = "%H:%M:%S %d/%m/%y") const;

      //##ModelId=3C8F18500073
      operator bool () const;

      //##ModelId=3C8C9EAA005B
      bool operator ! () const;

      //##ModelId=3D1C35690126
      double seconds () const;

      //##ModelId=3C9F3EF20221
      operator double () const;

      //##ModelId=3C7F3D500287
      Timestamp & operator += (const Timestamp &other);

      //##ModelId=3C7F3D720312
      Timestamp & operator -= (const Timestamp &other);

      //##ModelId=3C7F3D7800CC
      Timestamp operator + (const Timestamp &other) const;

      //##ModelId=3C7F3D7E032D
      Timestamp operator - (const Timestamp &other) const;

      //##ModelId=3C7F3E68035C
      void normalize ();

    //##ModelId=3DB934F000C7
      long sec () const;

    //##ModelId=3DB934F0030B
      long usec () const;

    // Additional Public Declarations
      // constructs from a struct timeval
    //##ModelId=3DB934F1014A
      Timestamp (const struct timeval &tv);
      
      // converts to a struct timeval
    //##ModelId=3DB934F201A5
      void to_timeval ( struct timeval &tv ) const;
    //##ModelId=3DB934F4020F
      operator struct timeval () const;
      
      // resets to 0
    //##ModelId=3DB934F50134
      void reset ();
      
      //  multiplies/divides by scalar
    //##ModelId=3DB934F50260
      Timestamp & operator *= (double x);
      
    //##ModelId=3DB934F70275
      Timestamp & operator /= (double x)
      { return *this *= (1/x); }
      
    //##ModelId=3DB934F900BD
      Timestamp operator * (double x) const
      { Timestamp res = *this; return res *= x; }
      
    //##ModelId=3DB934FA01AF
      Timestamp operator / (double x) const
      { Timestamp res = *this; return res /= x; }
      
      
    //##ModelId=3DB934FB02D3
      string toString (TimeUnits units,int prec = -1) const;
      

  private:
    // Data Members for Class Attributes

      //##ModelId=3C7F3B2600B2
      long sec_;

      //##ModelId=3C7F3B2E001D
      long usec_;

      //##ModelId=3C8F68EA004C
      static Timestamp tsnow;

};

//##ModelId=3C95AC350111

typedef Timestamp Timeval;
// Class Timestamp 

//##ModelId=3C7F3B580321
inline Timestamp::Timestamp()
{
  // default constructor: current time
  Timestamp::now(this);
}

//##ModelId=3C95C5F90389
inline Timestamp::Timestamp (long sec1, long usec1)
  : sec_(sec1),usec_(usec1)
{
}


//##ModelId=3DB934EA0370
inline bool Timestamp::operator==(const Timestamp &right) const
{
  return sec_ == right.sec_ && usec_ == right.usec_;
}

//##ModelId=3DB934EB0259
inline bool Timestamp::operator!=(const Timestamp &right) const
{
  return !((*this) == right);
}


//##ModelId=3DB934EC0142
inline bool Timestamp::operator<(const Timestamp &right) const
{
  return sec_ == right.sec_ ? usec_ < right.usec_ : sec_ < right.sec_;
}

inline bool Timestamp::operator>(const Timestamp &right) const
{
  return sec_ == right.sec_ ? usec_ > right.usec_ : sec_ > right.sec_;
}

//##ModelId=3DB934EE004C
inline bool Timestamp::operator<=(const Timestamp &right) const
{
  return sec_ == right.sec_ ? usec_ <= right.usec_ : sec_ < right.sec_;
}

//##ModelId=3DB934EE03B3
inline bool Timestamp::operator>=(const Timestamp &right) const
{
  return sec_ == right.sec_ ? usec_ >= right.usec_ : sec_ > right.sec_;
}



//##ModelId=3D1C34DB0237
inline Timestamp Timestamp::delta (const Timestamp &start)
{
  return now() - start;
}

//##ModelId=3C8F18500073
inline Timestamp::operator bool () const
{
  return sec_ || usec_;
}

//##ModelId=3C8C9EAA005B
inline bool Timestamp::operator ! () const
{
  return ! static_cast<bool>(*this);
}

//##ModelId=3D1C35690126
inline double Timestamp::seconds () const
{
  return sec_ + 1e-6*usec_;
}

//##ModelId=3C9F3EF20221
inline Timestamp::operator double () const
{
  return seconds();
}

//##ModelId=3C7F3D7800CC
inline Timestamp Timestamp::operator + (const Timestamp &other) const
{
  Timestamp res = *this;
  return res += other;
}

//##ModelId=3C7F3D7E032D
inline Timestamp Timestamp::operator - (const Timestamp &other) const
{
  Timestamp res = *this;
  return res -= other;
}

//##ModelId=3DB934F000C7
inline long Timestamp::sec () const
{
  return sec_;
}

//##ModelId=3DB934F0030B
inline long Timestamp::usec () const
{
  return usec_;
}

//##ModelId=3DB934F1014A
inline Timestamp::Timestamp (const struct timeval &tv)
{ 
  sec_ = tv.tv_sec; 
  usec_ = tv.tv_usec; 
}

//##ModelId=3DB934F201A5
inline void Timestamp::to_timeval ( struct timeval &tv ) const
{
  tv.tv_sec = sec_; 
  tv.tv_usec = usec_;
}

// converts to a struct timeval
//##ModelId=3DB934F4020F
inline Timestamp::operator struct timeval () const
{ 
  struct timeval tv = { sec_,usec_ }; 
  return tv;
}

// resets to 0
//##ModelId=3DB934F50134
inline void Timestamp::reset ()
{ sec_ = usec_ = 0; }


};
#endif
