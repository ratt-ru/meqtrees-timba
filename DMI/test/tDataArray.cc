#include "DataArray.h"
#include "DataRecord.h"
#include "Debug.h"
#include <aips/Arrays/ArrayMath.h>

int main()
{
  try {
    DataRecord rec;
    rec["A"] <<= new DataArray(TpArray_float, IPosition(2,10,12));
    float* ptr1 = rec["A/5.5"].as_float_wp();
    Array_float* farr = &rec["A"];
    Assert (farr->nelements() == 20*12);
    indgen (*farr);
    float* ptr = &rec["A"];
    for (int i=0; i<10*12; i++) {
      Assert (ptr[i] == i);
    }
  } catch (Debug::Error& x) {
    cerr << x.what() << endl;
    return 1;
  }
  return 0;
}
