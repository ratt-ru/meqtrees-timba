//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef AtomicID_h
#define AtomicID_h 1

#include "Common.h"
#include <map>

// Registry
#include "DMI/Registry.h"
#pragma aidgroup DMI
#pragma aid A B C D E F G H I J K L M N O P Q R S T U V W X Y Z


//##ModelId=3BE970170297
//##Documentation
//## Atomic identifier (numeric, but with a mapping mechanism to symbolic
//## IDs)

class AtomicID 
{
  public:
      //##ModelId=3BE970C40246
      AtomicID (int n = 0);

      //##ModelId=3C5E74CB0112
      //##Documentation
      //## Constructs AtomicID by its name
      explicit AtomicID (const string &str);

      //##ModelId=3C68D5220318
      AtomicID (const char *str);

    //##ModelId=3DB93440027B
      bool operator==(const AtomicID &right) const;

    //##ModelId=3DB93440036C
      bool operator!=(const AtomicID &right) const;

    //##ModelId=3DB934410088
      bool operator<(const AtomicID &right) const;

    //##ModelId=3DB9344101BE
      bool operator>(const AtomicID &right) const;

    //##ModelId=3DB9344102E1
      bool operator<=(const AtomicID &right) const;

    //##ModelId=3DB934420043
      bool operator>=(const AtomicID &right) const;


      //##ModelId=3C0F8D1102B6
      operator int () const;

      //##ModelId=3C1A1A9000DD
      AtomicID & operator = (int n);

      //##ModelId=3C596562005C
      bool operator ! ();

      //##ModelId=3C1A28850258
      bool isAny () const;

      //##ModelId=3C1A288F0342
      bool isWildcard () const;

      //##ModelId=3C553EC402AA
      //##Documentation
      //## If AtomicID corresponds to an index, returns that index, else
      //## returns -1
      int index () const;

      //##ModelId=3C1DFD1A0235
      bool matches (const AtomicID &other) const;

      //##ModelId=3BE9709700A7
      string toString () const;

      //##ModelId=3C68D5ED01F8
      static int findName (const string &str);

    //##ModelId=3DB9344201DE
      int id () const;

    // Additional Public Declarations
    //##ModelId=3DB934420274
      bool operator==(int right) const;
    //##ModelId=3DB9344203E7
      bool operator!=(int right) const;
    //##ModelId=3DB934430199
      bool operator<(int right) const;
    //##ModelId=3DB93443033E
      bool operator>(int right) const;
    //##ModelId=3DB934440119
      bool operator<=(int right) const;
    //##ModelId=3DB9344402F9
      bool operator>=(int right) const;
  private:
    // Additional Private Declarations
    //##ModelId=3DB934450106
      DeclareBiRegistry(AtomicID,int,string);
  private:
    // Data Members for Class Attributes

      //##ModelId=3BE9706902BD
      int aid;

};

// some special AtomicIDs
const AtomicID AidNull(0),
               AidAny(-1),        // "?" 
               AidWildcard(-2),   // "*"
               AidSlash(-3),      // "/"
               AidRange(-4),      // ":"
               AidEmpty(-5);      // "" (zero-length string)

//##ModelId=3C553F440092
//##Documentation
//## AidIndex is a helper class which may be used to create an AtomicID
//## corresponding to an array index
class AidIndex : public AtomicID
{
  public:
      //##ModelId=3C553F7100D2
      AidIndex (int index = 0);

};

// Class AtomicID 

//##ModelId=3BE970C40246
inline AtomicID::AtomicID (int n)
    : aid(n)
{
}

//##ModelId=3C5E74CB0112
inline AtomicID::AtomicID (const string &str)
  : aid( findName(str) )
{
  FailWhen(!aid && (!str.length() || str[0] != '0') ,"Unknown AtomicID `"+str+"'");
}

//##ModelId=3C68D5220318
inline AtomicID::AtomicID (const char *str)
  : aid( findName(str) )
{
}


//##ModelId=3DB93440027B
inline bool AtomicID::operator==(const AtomicID &right) const
{
  return aid == right.aid;
}

//##ModelId=3DB93440036C
inline bool AtomicID::operator!=(const AtomicID &right) const
{
  return aid != right.aid;
}


//##ModelId=3DB934410088
inline bool AtomicID::operator<(const AtomicID &right) const
{
  return aid < right.aid;
}

inline bool AtomicID::operator>(const AtomicID &right) const
{
  return aid > right.aid;
}

//##ModelId=3DB9344102E1
inline bool AtomicID::operator<=(const AtomicID &right) const
{
  return aid <= right.aid;
}

//##ModelId=3DB934420043
inline bool AtomicID::operator>=(const AtomicID &right) const
{
  return aid >= right.aid;
}



//##ModelId=3C0F8D1102B6
inline AtomicID::operator int () const
{
  return aid;
}

//##ModelId=3C1A1A9000DD
inline AtomicID & AtomicID::operator = (int n)
{
  aid = n;
  return *this;
}

//##ModelId=3C596562005C
inline bool AtomicID::operator ! ()
{
  return !aid;
}

//##ModelId=3C1A28850258
inline bool AtomicID::isAny () const
{
  return aid == (int) AidAny; 
}

//##ModelId=3C1A288F0342
inline bool AtomicID::isWildcard () const
{
  return aid == (int) AidWildcard; 
}

//##ModelId=3C553EC402AA
inline int AtomicID::index () const
{
  return aid >= 0 ? aid : -1;
}

//##ModelId=3C1DFD1A0235
inline bool AtomicID::matches (const AtomicID &other) const
{
  return isAny() || isWildcard() ||
         other.isAny() || other.isWildcard() ||
         aid == other.aid;
}

//##ModelId=3DB9344201DE
inline int AtomicID::id () const
{
  return aid;
}

// Class AidIndex 

//##ModelId=3C553F7100D2
inline AidIndex::AidIndex (int index)
  : AtomicID( index )
{
}


//##ModelId=3DB934420274
inline bool AtomicID::operator==(int right) const
{
  return aid == right;
}
//##ModelId=3DB9344203E7
inline bool AtomicID::operator!=(int right) const
{
  return aid != right;
}
//##ModelId=3DB934430199
inline bool AtomicID::operator<(int right) const
{
  return aid < right;
}
inline bool AtomicID::operator>(int right) const
{
  return aid > right;
}
//##ModelId=3DB934440119
inline bool AtomicID::operator<=(int right) const
{
  return aid <= right;
}
//##ModelId=3DB9344402F9
inline bool AtomicID::operator>=(int right) const
{
  return aid >= right;
}



#endif
