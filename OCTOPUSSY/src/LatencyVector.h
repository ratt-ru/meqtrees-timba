#ifndef LatencyVector_h
#define LatencyVector_h 1

#include <vector>
#include <utility>
#include <string>
#include "DMI/Timestamp.h"
    
using std::vector;
using std::pair;
using std::make_pair;    
using std::string;

//##ModelId=3DB958F10229
class LatencyVector
{
  public:
    //##ModelId=3DB958F10230
    typedef pair<Timestamp,string> Entry;
  
  private:
    //##ModelId=3DB958F3006B
    Timestamp tms0;
    //##ModelId=3DB958F3007D
    vector<Entry> tms;
    
    //##ModelId=3DB958F10235
    typedef vector<Entry>::iterator VEI;
    //##ModelId=3DB958F1023A
    typedef vector<Entry>::const_iterator CVEI;
    
  public:
    //##ModelId=3DB958F30090
    LatencyVector ()
    { Timestamp::now(&tms0); tms.reserve(5); }
  
    // resets the clock
    //##ModelId=3DB958F30091
    void reset ()
    { Timestamp::now(&tms0); }
    
    // resets clock & all values
    //##ModelId=3DB958F30092
    void clear ()
    { tms.resize(0); reset(); }
  
    // adds an explicit measurement to the vector
    //##ModelId=3DB958F30094
    void add (const Timestamp &value,const string &desc = "")
    { tms.push_back( make_pair(value-tms0,desc) ); tms0 = value; }
    
    // measures & adds a value since the last measurement
    //##ModelId=3DB958F300B9
    void measure (const string &desc = "")
    { add(Timestamp(),desc); }

    // returns number of values
    //##ModelId=3DB958F300CD
    int size () const
    { return tms.size(); }

    // returns n-th value
    //##ModelId=3DB958F300CF
    Timestamp value (uint n) const
    { return n < tms.size() ? tms[n].first : Timestamp(0,0); }

    // returns n-th description
    //##ModelId=3DB958F300E3
    string desc (uint n) const
    { return n < tms.size() ? tms[n].second : ""; }
    
    // returns sum of all values
    //##ModelId=3DB958F300F8
    Timestamp total () const;
    
    // adds two latency vectors together
    //##ModelId=3DB958F300FA
    LatencyVector & operator += ( const LatencyVector & other );
    
    // divides latency vector by some value
    //##ModelId=3DB958F3010D
    LatencyVector & operator /= ( double x );
    
    // returns values in vector form
    //##ModelId=3DB958F30120
    string toString() const;
    
    // pack/unpack interface
    //##ModelId=3DB958F30122
    size_t pack (void *block,size_t &nleft) const;
    //##ModelId=3DB958F30148
    void unpack (const void *block,size_t sz);
    //##ModelId=3DB958F3016C
    size_t packSize () const;
};

// the DummyLatencyVector class provides the interface of LatencyVector,
// but as inlined no-ops
//##ModelId=3DB958F101C6
class DummyLatencyVector
{
  private:
    
  public:
    //##ModelId=3DB958F2029B
    DummyLatencyVector () {};
  
    // resets the clock
    //##ModelId=3DB958F2029C
    void reset () {};
    
    // resets clock & all values
    //##ModelId=3DB958F2029E
    void clear () {};
  
    // adds an explicit measurement to the vector
    //##ModelId=3DB958F2029F
    void add (const Timestamp &,const string & = "") {};
    
    // measures & adds a value since the last measurement
    //##ModelId=3DB958F202A3
    void measure (const string & = "") {};

    // returns number of values
    //##ModelId=3DB958F202A5
    int size () const 
    { return 0; }

    // returns n-th value
    //##ModelId=3DB958F202A7
    Timestamp value (uint) const
    { return 0; }

    // returns n-th description
    //##ModelId=3DB958F202AA
    string desc (uint) const
    { return ""; }
    
    // returns sum of all values
    //##ModelId=3DB958F202AD
    Timestamp total () const { return Timestamp(0,0); }
    
    // adds two latency vectors together
    //##ModelId=3DB958F202AF
    DummyLatencyVector & operator += ( const LatencyVector & ) { return *this; }
    
    // divides latency vector by some value
    //##ModelId=3DB958F202B1
    DummyLatencyVector & operator /= ( double ) { return *this; }
    
    // returns values in vector form
    //##ModelId=3DB958F202B3
    string toString() const { return ""; }
};

#endif
