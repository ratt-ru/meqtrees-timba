#include "DMI/DataArray.h"
#include "DMI/DataRecord.h"
#include "Common/Debug.h"
#include <aips/Arrays/ArrayMath.h>
#include <aips/Arrays/ArrayLogical.h>

int main()
{
  try {
    DataRecord rec;
    rec["A"] <<= new DataArray(TpArray_float, IPosition(2,10,12));
    DataArray* dtarr = &rec["A"];
    DataArray* dtarr1 = rec["A"].as_DataArray_wp();
    Assert (dtarr == dtarr1);
    Assert (dtarr->objectType() == TpDataArray);
    Assert (dtarr->type() == TpArray_float);
    Array_float farr = rec["A"];
    Assert (farr.nelements() == 10*12);
    indgen (farr);
    const float* ptr = &rec["A/0.0"];
    const float* ptr1= rec["A/0.0"].as_float_p();
    Assert (ptr == ptr1);
    const float* ptr2 = &rec["A"];
    Assert (ptr == ptr2);
    bool deleteIt;
    Assert (ptr == farr.getStorage(deleteIt));

    for (int i=0; i<10*12; i++) {
      Assert (ptr[i] == i);
    }
    try {
      cout << endl << "Expect type mismatch exception ..." << endl;
      cout << ">>>" << endl;
      rec["A"].as_Array_double();
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
      cout << "<<<" << endl;
    }
    try {
      cout << endl << "Expect type mismatch exception ..." << endl;
      cout << ">>>" << endl;
      rec["A"].as_double_wp();
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
      cout << "<<<" << endl;
    }

    // Convert some HIID's to start,end,incr.
    IPosition start,end,incr,keep;
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
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID("10."), start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".12"), start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".10:9"), start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".9:10:0"), start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (HIID(".."), start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (AidRange, start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (1 | AidRange | AidRange, start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }
    try {
      dtarr->parseHIID (1 | AidRange, start, end, incr, keep);
    } catch (Debug::Error& x) {
      cout << x.what() << endl;
    }

    // Try getting a subset in x with the axis removed.
    {
      for (int i=0; i<10; i++) {
	float val=i;
	Array_float subarr = rec[HIID("A") | AidSlash | i | AidWildcard];
	Assert (subarr.shape() == IPosition(1,12));
	for (int j=0; j<12; j++) {
	  Assert (subarr(IPosition(1,j)) == val);
	  val+=10;
	}
      }
    }
    // Try getting a subset in x without the axis removed.
    {
      for (int i=0; i<10; i++) {
	float val=i;
	Array_float subarr = rec[HIID("A") | AidSlash | i | AidRange | i |
				 AidWildcard];
	Assert (subarr.shape() == IPosition(2,1,12));
	Assert (allEQ (subarr, farr(IPosition(2,i,0), IPosition(2,i,11))));
	for (int j=0; j<12; j++) {
	  Assert (subarr(IPosition(2,0,j)) == val);
	  val+=10;
	}
      }
    }
    // Try getting a subset in y with the axis removed.
    {
      float val = 0;
      for (int i=0; i<12; i++) {
	Array_float subarr = rec[HIID("A") | AidSlash | AidWildcard | i];
	Assert (subarr.shape() == IPosition(1,10));
	for (int j=0; j<10; j++) {
	  Assert (subarr(IPosition(1,j)) == val);
	  val++;
	}
      }
    }
    // Try getting a subset in y without the axis removed.
    {
      float val = 0;
      for (int i=0; i<12; i++) {
	Array_float subarr = rec[HIID("A") | AidSlash | AidWildcard | i |
				 AidRange | i];
	Assert (subarr.shape() == IPosition(2,10,1));
	Assert (allEQ (subarr, farr(IPosition(2,0,i), IPosition(2,9,i))));
	for (int j=0; j<10; j++) {
	  Assert (subarr(IPosition(2,j,0)) == val);
	  val++;
	}
      }
    }
  } catch (Debug::Error& x) {
    cerr << x.what() << endl;
    return 1;
  }
  return 0;
}
