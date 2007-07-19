//  Lonumerics.h: Define numeric types
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#ifndef COMMON_LONUMERICS_H
#define COMMON_LONUMERICS_H 1

#include <TimBase/LofarTypes.h>
#include <TimBase/lofar_complex.h>

using LOFAR::fcomplex;
using LOFAR::dcomplex;

// Numeric_zero returns a 0 for any type
// Because the C99 _Complex cannot be initialized with a 0, it will have explicit
// specializations
template<typename T>
inline T numeric_zero (T* =0)
{ return 0; }

// add complex ops depending on compiler
#if __GNUC__ >= 3 && !USE_STD_COMPLEX

  inline fcomplex make_fcomplex (float r,float i=0.)
  { return r + 1i*i; }

  inline dcomplex make_dcomplex (double r,double i=0.)
  { return r + 1i*i; }

  inline float creal (fcomplex arg)
  { return __real__ arg; }
  inline float cimag (fcomplex arg)
  { return __imag__ arg; }
  inline float abs (fcomplex arg)
  { return __builtin_cabsf(arg); }
  inline double creal (dcomplex arg)
  { return __real__ arg; }
  inline double cimag (dcomplex arg)
  { return __imag__ arg; }
  inline double abs (dcomplex arg)
  { return __builtin_cabs(arg); }
  
  template<>
  inline fcomplex numeric_zero (fcomplex *)
  { return 0.0fi; }
  
  template<>
  inline dcomplex numeric_zero (dcomplex *)
  { return 0.0fi; }
  
#else        

  inline fcomplex make_fcomplex (float r,float i)
  { return fcomplex(r,i); }

  inline dcomplex make_dcomplex (double r,double i)
  { return dcomplex(r,i); }

  typedef<typename T>
  inline T creal (const std::complex<T> &arg)
  { return arg.real(); }

  typedef<typename T>
  inline T cimag (const std::complex<T> &arg)
  { return arg.real(); }
#endif
    
    

#ifndef DoForAllNumericTypes
// 
// The DoForAllNumericTypes macros allows you to repeat a section of code
// for all numeric types. 
//
// To do this, first define a two-argument macro do_something(type,arg) 
// that expands to whatever it is you want repeated (do_something can be 
// any name). Then, invoke DoForAllNumericTypes(do_something,arg). This
// repeatedly expands your do_something() macro for all values of "type".
// The "arg" parameter can be used to pass in an additional argument, you
// may simply ignore it if you don't need it.
// 
// The macro comes in three vesrions:
//      DoForAllNumericTypes(Do,arg) expands Do(type,arg) for all types,
//              separated by semicolons, with a trailing semicolon
//      DoForAllNumericTypes1(Do,arg) expands Do(type,arg) for all types,
//              separated by commas, no trailing comma (useful for, e.g.,
//              initializer lists)
//      DoForAllNumericTypes_Sep(Do,arg,sep) expands Do(type,arg) for all types,
//              separated by the "sep" argument. without a trailing separator
#define DoForAllNumericTypes_Sep(Do,arg,sep) \
            Do(bool,arg) sep \
            Do(char,arg) sep \
            Do(uchar,arg) sep \
            Do(short,arg) sep \
            Do(ushort,arg) sep \
            Do(int,arg) sep \
            Do(uint,arg) sep \
            Do(long,arg) sep \
            Do(ulong,arg) sep \
            Do(longlong,arg) sep \
            Do(ulonglong,arg) sep \
            Do(float,arg) sep \
            Do(double,arg) sep \
            Do(ldouble,arg) sep \
            Do(fcomplex,arg) sep \
            Do(dcomplex,arg)
            
#define DoForAllNumericTypes(Do,arg) DoForAllNumericTypes_Sep(Do,arg,;)
        
#define DoForAllNumericTypes1(Do,arg) \
        Do(bool,arg) , \
        Do(char,arg) , \
        Do(uchar,arg) , \
        Do(short,arg) , \
        Do(ushort,arg) , \
        Do(int,arg) , \
        Do(uint,arg) , \
        Do(long,arg) , \
        Do(ulong,arg) , \
        Do(longlong,arg) , \
        Do(ulonglong,arg) , \
        Do(float,arg) , \
        Do(double,arg) , \
        Do(ldouble,arg) , \
        Do(fcomplex,arg) , \
        Do(dcomplex,arg)
        
#endif


#endif
