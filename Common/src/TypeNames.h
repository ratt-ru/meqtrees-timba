//# TypeNames.h: Return a string giving the type name to be stored in blobs
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#ifndef COMMON_TYPENAMES_H
#define COMMON_TYPENAMES_H

//# Includes
#include <Common/LofarTypes.h>
#include <string>

namespace LOFAR
{
// These global functions return the name of the basic types.
// They are meant to get the full id of a templated class when such an
// object is stored in a blob.
// \defgroup TypeNames global type name functions
// <group>

  // Give the name of the basic types.
  // <group>
  const std::string& typeName (const void*);
  const std::string& typeName (const bool*);
  const std::string& typeName (const char*);
  const std::string& typeName (const uchar*);
  const std::string& typeName (const int16*);
  const std::string& typeName (const uint16*);
  const std::string& typeName (const int32*);
  const std::string& typeName (const uint32*);
  const std::string& typeName (const int64*);
  const std::string& typeName (const uint64*);
  const std::string& typeName (const float*);
  const std::string& typeName (const double*);
  const std::string& typeName (const fcomplex*);
  const std::string& typeName (const dcomplex*);
  template<typename T> const std::string& typeName (const std::complex<T>*);
  template<typename T> const std::string& typeName (T**);
  // </group>

// </group>
}

// Include templated implementations.
#include <Common/TypeNames.tcc>


#endif
