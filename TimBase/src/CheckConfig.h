//#  CheckConfig.h: Macros for declaring a config-dependent data structure.
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef LOFAR_COMMON_CHECKCONFIG_H
#define LOFAR_COMMON_CHECKCONFIG_H

// The CHECK_CONFIG macros should be used if and when you declare a
// config-dependent data structure. These allow you to automatically insert
// symbol references into your object files that will be checked for
// consistency at link time.
    

// If you declare a config-dependent data structure, you should insert a 
// CHECK_CONFIG(ID,KEY,VALUE) declaration into the header file. 
// This will generate an external reference to the symbol 
//      __REQUIRE_KEY_VALUE__
// in each object file that includes this header.
// ID should be a unique ID (e.g., the name of your data structure), this is
// required to generate a unique name for a static variable that will not clash
// with possible other CHECK_CONFIGs invocations.
        
#define CHECK_CONFIG(id,key,val) extern int __REQUIRE_##key##_##val##__; \
  static int __check_config_##key##_##id = __REQUIRE_##key##_##val##__;

// A corresponding CHECK_CONFIG_CC(KEY,VALUE) declaration should be present
// in some .cc file, this generates the symbol
//    __REQUIRE_KEY_VALUE__
#define CHECK_CONFIG_CC(key,val) int __REQUIRE_##key##_##val##__; 

// Check Common/Thread.h and Common/Thread/Thread.cc for examples of how this 
// works.

#endif
