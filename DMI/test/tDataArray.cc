#include "DMI/NumArray.h"
#include "DMI/Record.h"
#include "TimBase/Debug.h"
//#include <casa/Arrays/ArrayMath.h>
//#include <casa/Arrays/ArrayLogical.h>

using namespace DebugDefault;
using namespace DMI;
        
template<class T>
inline ostream & operator << (ostream &str,const vector<T> &vec )
{
  str << "[ ";
  for( typename vector<T>::const_iterator iter = vec.begin(); 
       iter != vec.end(); iter++ )
    str << *iter << " ";
  return str << "]";
}

int main()
{
  try {
    DMI::Record rec;
    rec["A"] <<= new DMI::NumArray(Tpfloat,makeLoShape(10,12));
    DMI::NumArray* dtarr = rec["A"].as_wp<DMI::NumArray>();
//    DMI::NumArray* dtarr1 = rec["A"].as_wp<DMI::NumArray>();
//    Assert (dtarr == dtarr1);
    Assert (dtarr->objectType() == TpDMINumArray);
    Assert (dtarr->type() == TpArray(Tpfloat,2));
    LoMat_float farr = rec["A"];
    Assert (farr.size() == 10*12);
    
    farr = blitz::tensor::i + blitz::tensor::j*10;
    
    const float* ptr = &rec["A/0.0"];
    const float* ptr1= rec["A/0.0"].as_p<float>();
    Assert (ptr == ptr1);
    const float* ptr2 = &rec["A"];
    Assert (ptr == ptr2);
    
//     bool deleteIt;
//     Assert (ptr == farr.getStorage(deleteIt));
//     for (int i=0; i<10*12; i++) {
//       Assert (ptr[i] == i);
//     }
    
    try {
      cout << endl << "Expect type mismatch exception ..." << endl;
      cout << ">>>" << endl;
      rec["A"].as<LoMat_double>();
    } catch (std::exception& x) {
      cout << x.what() << endl;
      cout << "<<<" << endl;
    }
    try {
      cout << endl << "Expect type mismatch exception ..." << endl;
      cout << ">>>" << endl;
      rec["A"].as_wp<double>();
    } catch (std::exception& x) {
      cout << x.what() << endl;
      cout << "<<<" << endl;
    }

    // Convert some HIID's to start,end,incr.
    LoPos start,end,incr;
    vector<bool> keep;
    cout << dtarr->parseHIID (HIID("."), start, end, incr, keep);
    cout << start << end << incr << keep << endl;
    cout << dtarr->parseHIID (HIID("1.2"), start, end, incr, keep);
    cout << start << end << incr << keep << endl;
    cout << dtarr->parseHIID (HIID("1."), start, end, incr, keep);
    cout << start << end << incr << keep << endl;
    cout << dtarr->parseHIID (HIID(".2"), start, end, incr, keep);
    cout << start << end << incr << keep << endl;
    cout << dtarr->parseHIID (HIID("1:3.::2"), start, end, incr, keep);
    cout << start << end << incr << keep << endl;
    cout << endl << "Expect some HIID parser exceptions ..." << endl;
    try {
      dtarr->parseHIID (HIID("1:3.:::2"), start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID("10."), start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".12"), start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".10:9"), start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".9:10:0"), start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".."), start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (AidRange, start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (1 | AidRange | AidRange, start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (1 | AidRange, start, end, incr, keep);
    } catch (std::exception& x) {
      cout << x.what() << endl;
    }

    // Try getting a subset in x with the axis removed.
    {
      for (int i=0; i<10; i++) 
      {
        float val=i;
        LoVec_float subarr = rec[HIID("A") | AidSlash | i | AidWildcard];
        Assert( subarr.shape() == LoShape(12) );
        for (int j=0; j<12; j++) 
        {
          Assert( subarr(j) == val );
          val += 10;
        }        
      }
    }
    // Try getting a subset in x without the axis removed.
    {
      for (int i=0; i<10; i++) 
      {
	      float val=i;
        LoMat_float subarr = rec[HIID("A") | AidSlash | i | AidRange | i | AidWildcard];
	      Assert( subarr.shape() == LoShape(1,12) );
	      Assert( all( subarr == farr(LoRange(i,i),LoRange::all()) ) );
        for (int j=0; j<12; j++) 
        {
	        Assert (subarr(0,j) == val);
	        val += 10;
        }
      }
    }
    // Try getting a subset in y with the axis removed.
    {
      float val = 0;
      for (int i=0; i<12; i++) 
      {
        LoVec_float subarr = rec[HIID("A/*") | i];
        Assert(subarr.shape() == LoShape(10));
        for (int j=0; j<10; j++) 
        {
	        Assert(subarr(j) == val);
	        val++;
        }
      }
    }
    // Try getting a subset in y without the axis removed.
    {
      float val = 0;
      for (int i=0; i<12; i++) 
      {
        LoMat_float subarr = rec[HIID("A/*") | i | AidRange | i];
        Assert(subarr.shape() == LoShape(10,1));
        Assert(all(subarr ==  farr(LoRange::all(),LoRange(i,i))));
        for (int j=0; j<10; j++) 
        {
	        Assert( subarr(j,0) == val);
	        val++;
        }
      }
    }
  } catch (std::exception& x) {
    cerr << x.what() << endl;
    return 1;
  }
  return 0;
}
