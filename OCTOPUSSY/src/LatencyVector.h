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

class LatencyVector
{
  public:
    typedef pair<Timestamp,string> Entry;
  
  private:
    Timestamp tms0;
    vector<Entry> tms;
    
    typedef vector<Entry>::iterator VEI;
    typedef vector<Entry>::const_iterator CVEI;
    
  public:
    LatencyVector ()
    { Timestamp::now(&tms0); tms.reserve(5); }
  
    // resets the clock
    void reset ()
    { Timestamp::now(&tms0); }
    
    // resets clock & all values
    void clear ()
    { tms.resize(0); reset(); }
  
    // adds an explicit measurement to the vector
    void add (const Timestamp &value,const string &desc = "")
    { tms.push_back( make_pair(value-tms0,desc) ); tms0 = value; }
    
    // measures & adds a value since the last measurement
    void measure (const string &desc = "")
    { add(Timestamp(),desc); }

    // returns number of values
    int size () const
    { return tms.size(); }

    // returns n-th value
    Timestamp value (uint n) const
    { return n < tms.size() ? tms[n].first : Timestamp(0,0); }

    // returns n-th description
    string desc (uint n) const
    { return n < tms.size() ? tms[n].second : ""; }
    
    // returns sum of all values
    Timestamp total () const;
    
    // adds two latency vectors together
    LatencyVector & operator += ( const LatencyVector & other );
    
    // divides latency vector by some value
    LatencyVector & operator /= ( double x );
    
    // returns values in vector form
    string toString() const;
    
    // pack/unpack interface
    size_t pack (void *block,size_t &nleft) const;
    void unpack (const void *block,size_t sz);
    size_t packSize () const;
};

// the DummyLatencyVector class provides the interface of LatencyVector,
// but as inlined no-ops
class DummyLatencyVector
{
  private:
    
  public:
    DummyLatencyVector () {};
  
    // resets the clock
    void reset () {};
    
    // resets clock & all values
    void clear () {};
  
    // adds an explicit measurement to the vector
    void add (const Timestamp &,const string & = "") {};
    
    // measures & adds a value since the last measurement
    void measure (const string & = "") {};

    // returns number of values
    int size () const 
    { return 0; }

    // returns n-th value
    Timestamp value (uint) const
    { return 0; }

    // returns n-th description
    string desc (uint) const
    { return ""; }
    
    // returns sum of all values
    Timestamp total () const { return Timestamp(0,0); }
    
    // adds two latency vectors together
    DummyLatencyVector & operator += ( const LatencyVector & ) { return *this; }
    
    // divides latency vector by some value
    DummyLatencyVector & operator /= ( double ) { return *this; }
    
    // returns values in vector form
    string toString() const { return ""; }
};

#endif
