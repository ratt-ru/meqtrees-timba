//  lofar_complex.h:
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

#ifndef COMMON_COMPLEX_H
#define COMMON_COMPLEX_H

#ifdef USE_STD_COMPLEX

#include <complex>

namespace LOFAR
{
  using std::complex;
  using std::sin;
  using std::cos;
  using std::tan;
  using std::exp;
  using std::sqrt;
//   using std::conj;
}

#ifdef MAKE_LOFAR_SYMBOLS_GLOBAL
#include <TimBase/lofar_global_symbol_warning.h>
using LOFAR::complex;
using LOFAR::sin;
using LOFAR::cos;
using LOFAR::tan;
using LOFAR::exp;
using LOFAR::sqrt;
// using LOFAR::conj;
using std::conj;
#endif

#endif

#endif
