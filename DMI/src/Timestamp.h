//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7F3B770339.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7F3B770339.cm

//## begin module%3C7F3B770339.cp preserve=no
//## end module%3C7F3B770339.cp

//## Module: Timestamp%3C7F3B770339; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar9\oms\LOFAR\src-links\DMI\Timestamp.h

#ifndef Timestamp_h
#define Timestamp_h 1

//## begin module%3C7F3B770339.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3C7F3B770339.additionalIncludes

//## begin module%3C7F3B770339.includes preserve=yes
#include <sys/time.h>
//## end module%3C7F3B770339.includes

//## begin module%3C7F3B770339.declarations preserve=no
//## end module%3C7F3B770339.declarations

//## begin module%3C7F3B770339.additionalDeclarations preserve=yes
#pragma types :Timestamp
//## end module%3C7F3B770339.additionalDeclarations


//## begin Timestamp%3C7F3B1D025E.preface preserve=yes
//## end Timestamp%3C7F3B1D025E.preface

//## Class: Timestamp%3C7F3B1D025E
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class Timestamp 
{
  //## begin Timestamp%3C7F3B1D025E.initialDeclarations preserve=yes
  //## end Timestamp%3C7F3B1D025E.initialDeclarations

  public:
    //## Constructors (generated)
      Timestamp();

    //## Constructors (specified)
      //## Operation: Timestamp%3C7F3B580321
      explicit Timestamp (long sec1, long usec1 = 0);

      //## Operation: Timestamp%3C95C5F90389
      Timestamp (double sec1);

    //## Equality Operations (generated)
      bool operator==(const Timestamp &right) const;

      bool operator!=(const Timestamp &right) const;

    //## Relational Operations (generated)
      bool operator<(const Timestamp &right) const;

      bool operator>(const Timestamp &right) const;

      bool operator<=(const Timestamp &right) const;

      bool operator>=(const Timestamp &right) const;


    //## Other Operations (specified)
      //## Operation: now%3C8F67DD00BD
      static const Timestamp & now (Timestamp *pts = &Timestamp::tsnow);

      //## Operation: delta%3D1C34DB0237
      static Timestamp delta (const Timestamp &start);

      //## Operation: toString%3CA06AE50335
      string toString (const char *format = "%H:%M:%S %d/%m/%y") const;

      //## Operation: operator bool%3C8F18500073
      operator bool () const;

      //## Operation: operator !%3C8C9EAA005B
      bool operator ! () const;

      //## Operation: seconds%3D1C35690126
      double seconds () const;

      //## Operation: operator double%3C9F3EF20221
      operator double () const;

      //## Operation: operator +=%3C7F3D500287
      Timestamp & operator += (const Timestamp &other);

      //## Operation: operator -=%3C7F3D720312
      Timestamp & operator -= (const Timestamp &other);

      //## Operation: operator +%3C7F3D7800CC
      Timestamp operator + (const Timestamp &other) const;

      //## Operation: operator -%3C7F3D7E032D
      Timestamp operator - (const Timestamp &other) const;

      //## Operation: normalize%3C7F3E68035C
      void normalize ();

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: sec%3C7F3B2600B2
      long sec () const;

      //## Attribute: usec%3C7F3B2E001D
      long usec () const;

    // Additional Public Declarations
      //## begin Timestamp%3C7F3B1D025E.public preserve=yes
      // constructs from a struct timeval
      Timestamp (const struct timeval &tv)
      { 
        sec_ = tv.tv_sec; 
        usec_ = tv.tv_usec; 
      }
      
      // converts to a struct timeval
      operator struct timeval ()
      { 
        struct timeval tv = { sec_,usec_ }; 
        return tv;
      }
      //## end Timestamp%3C7F3B1D025E.public

  protected:
    // Additional Protected Declarations
      //## begin Timestamp%3C7F3B1D025E.protected preserve=yes
      //## end Timestamp%3C7F3B1D025E.protected

  private:
    // Additional Private Declarations
      //## begin Timestamp%3C7F3B1D025E.private preserve=yes
      //## end Timestamp%3C7F3B1D025E.private

  private: //## implementation
    // Data Members for Class Attributes

      //## begin Timestamp::sec%3C7F3B2600B2.attr preserve=no  public: long {U} 
      long sec_;
      //## end Timestamp::sec%3C7F3B2600B2.attr

      //## begin Timestamp::usec%3C7F3B2E001D.attr preserve=no  public: long {U} 
      long usec_;
      //## end Timestamp::usec%3C7F3B2E001D.attr

      //## Attribute: tsnow%3C8F68EA004C
      //## begin Timestamp::tsnow%3C8F68EA004C.attr preserve=no  private: static Timestamp {U} 
      static Timestamp tsnow;
      //## end Timestamp::tsnow%3C8F68EA004C.attr

    // Additional Implementation Declarations
      //## begin Timestamp%3C7F3B1D025E.implementation preserve=yes
      //## end Timestamp%3C7F3B1D025E.implementation

};

//## begin Timestamp%3C7F3B1D025E.postscript preserve=yes
//## end Timestamp%3C7F3B1D025E.postscript

//## begin Timeval%3C95AC350111.preface preserve=yes
//## end Timeval%3C95AC350111.preface

//## Class: Timeval%3C95AC350111
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3C95AC4D02E2;Timestamp { -> }

typedef Timestamp Timeval;
//## begin Timeval%3C95AC350111.postscript preserve=yes
//## end Timeval%3C95AC350111.postscript

// Class Timestamp 

inline Timestamp::Timestamp()
  //## begin Timestamp::Timestamp%3C7F3B1D025E_const.hasinit preserve=no
  //## end Timestamp::Timestamp%3C7F3B1D025E_const.hasinit
  //## begin Timestamp::Timestamp%3C7F3B1D025E_const.initialization preserve=yes
  //## end Timestamp::Timestamp%3C7F3B1D025E_const.initialization
{
  //## begin Timestamp::Timestamp%3C7F3B1D025E_const.body preserve=yes
  // default constructor: current time
  Timestamp::now(this);
  //## end Timestamp::Timestamp%3C7F3B1D025E_const.body
}

inline Timestamp::Timestamp (long sec1, long usec1)
  //## begin Timestamp::Timestamp%3C7F3B580321.hasinit preserve=no
  //## end Timestamp::Timestamp%3C7F3B580321.hasinit
  //## begin Timestamp::Timestamp%3C7F3B580321.initialization preserve=yes
  : sec_(sec1),usec_(usec1)
  //## end Timestamp::Timestamp%3C7F3B580321.initialization
{
  //## begin Timestamp::Timestamp%3C7F3B580321.body preserve=yes
  //## end Timestamp::Timestamp%3C7F3B580321.body
}


inline bool Timestamp::operator==(const Timestamp &right) const
{
  //## begin Timestamp::operator==%3C7F3B1D025E_eq.body preserve=yes
  return sec_ == right.sec_ && usec_ == right.usec_;
  //## end Timestamp::operator==%3C7F3B1D025E_eq.body
}

inline bool Timestamp::operator!=(const Timestamp &right) const
{
  //## begin Timestamp::operator!=%3C7F3B1D025E_neq.body preserve=yes
  return !((*this) == right);
  //## end Timestamp::operator!=%3C7F3B1D025E_neq.body
}


inline bool Timestamp::operator<(const Timestamp &right) const
{
  //## begin Timestamp::operator<%3C7F3B1D025E_ls.body preserve=yes
  return sec_ == right.sec_ ? usec_ < right.usec_ : sec_ < right.sec_;
  //## end Timestamp::operator<%3C7F3B1D025E_ls.body
}

inline bool Timestamp::operator>(const Timestamp &right) const
{
  //## begin Timestamp::operator>%3C7F3B1D025E_gt.body preserve=yes
  return sec_ == right.sec_ ? usec_ > right.usec_ : sec_ > right.sec_;
  //## end Timestamp::operator>%3C7F3B1D025E_gt.body
}

inline bool Timestamp::operator<=(const Timestamp &right) const
{
  //## begin Timestamp::operator<=%3C7F3B1D025E_lseq.body preserve=yes
  return sec_ == right.sec_ ? usec_ <= right.usec_ : sec_ < right.sec_;
  //## end Timestamp::operator<=%3C7F3B1D025E_lseq.body
}

inline bool Timestamp::operator>=(const Timestamp &right) const
{
  //## begin Timestamp::operator>=%3C7F3B1D025E_gteq.body preserve=yes
  return sec_ == right.sec_ ? usec_ >= right.usec_ : sec_ > right.sec_;
  //## end Timestamp::operator>=%3C7F3B1D025E_gteq.body
}



//## Other Operations (inline)
inline Timestamp Timestamp::delta (const Timestamp &start)
{
  //## begin Timestamp::delta%3D1C34DB0237.body preserve=yes
  return now() - start;
  //## end Timestamp::delta%3D1C34DB0237.body
}

inline Timestamp::operator bool () const
{
  //## begin Timestamp::operator bool%3C8F18500073.body preserve=yes
  return sec_ || usec_;
  //## end Timestamp::operator bool%3C8F18500073.body
}

inline bool Timestamp::operator ! () const
{
  //## begin Timestamp::operator !%3C8C9EAA005B.body preserve=yes
  return ! static_cast<bool>(*this);
  //## end Timestamp::operator !%3C8C9EAA005B.body
}

inline double Timestamp::seconds () const
{
  //## begin Timestamp::seconds%3D1C35690126.body preserve=yes
  return sec_ + 1e-6*usec_;
  //## end Timestamp::seconds%3D1C35690126.body
}

inline Timestamp::operator double () const
{
  //## begin Timestamp::operator double%3C9F3EF20221.body preserve=yes
  return seconds();
  //## end Timestamp::operator double%3C9F3EF20221.body
}

inline Timestamp Timestamp::operator + (const Timestamp &other) const
{
  //## begin Timestamp::operator +%3C7F3D7800CC.body preserve=yes
  Timestamp res = *this;
  return res += other;
  //## end Timestamp::operator +%3C7F3D7800CC.body
}

inline Timestamp Timestamp::operator - (const Timestamp &other) const
{
  //## begin Timestamp::operator -%3C7F3D7E032D.body preserve=yes
  Timestamp res = *this;
  return res -= other;
  //## end Timestamp::operator -%3C7F3D7E032D.body
}

//## Get and Set Operations for Class Attributes (inline)

inline long Timestamp::sec () const
{
  //## begin Timestamp::sec%3C7F3B2600B2.get preserve=no
  return sec_;
  //## end Timestamp::sec%3C7F3B2600B2.get
}

inline long Timestamp::usec () const
{
  //## begin Timestamp::usec%3C7F3B2E001D.get preserve=no
  return usec_;
  //## end Timestamp::usec%3C7F3B2E001D.get
}

//## begin module%3C7F3B770339.epilog preserve=yes
//## end module%3C7F3B770339.epilog


#endif
