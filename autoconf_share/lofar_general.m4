#  lofar_general.m4: contains several general m4 functions
#
#  Copyright (C) 2002
#  ASTRON (Netherlands Foundation for Research in Astronomy)
#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#  $Id$

#
#  lofar_general.m4 contains the following m4 functions:
#    lofar_DEBUG_OPTIMIZE
#    lofar_CHECK_PRETTY_FUNCTION
#    lofar_CHECK_LONG_LONG
#

# lofar_DEBUG_OPTIMIZE
#
# Set debugging or optimisation flags for CC and CXX
#
# Please note that using --with-debug=-g and --with-optimize=-g have
# the same effect for the compiler. However, the first one also defines
# LOFAR_DEBUG in the config.h file, which the latter does not do.
# Also the first one enables DBGASSERT by default.
#
#
AC_DEFUN([lofar_DEBUG_OPTIMIZE],dnl
[dnl
AC_PREREQ(2.13)dnl
AC_ARG_WITH(debug,
	[  --with-debug     enable debugging C(XX)FLAGS (sets -g)],
	[with_debug="$withval"],
	[with_debug=no])dnl
AC_ARG_WITH(optimize,
	[  --with-optimize[=CFLAGS]  enable optimization C(XX)FLAGS (sets -O3 or +K3)],
	[with_optimize="$withval"],
	[with_optimize=no])dnl
AC_ARG_WITH(threads,
	[  --with-threads            enable support of threads],
	[with_threads="$withval"],
	[with_threads=no])dnl
AC_ARG_WITH(cppflags,
	[  --with-cppflags=CPPFLAGS  enable extra CPPFLAGS],
	[with_cppflags="$withval"])dnl
AC_ARG_WITH(cflags,
	[  --with-cflags=CFLAGS      enable extra CFLAGS],
	[with_cflags="$withval"])dnl
AC_ARG_WITH(cxxflags,
	[  --with-cxxflags=CXXFLAGS  enable extra CXXFLAGS],
	[with_cxxflags="$withval"])dnl
AC_ARG_WITH(ldflags,
	[  --with-ldflags=LDFLAGS    enable extra LDFLAGS],
	[with_ldflags="$withval"])dnl
AC_ARG_ENABLE(tracer,
	[  --disable-tracer        en/disable TRACER macros (default is debug/opt)],
	[enable_tracer="$enableval"],
	[enable_tracer="default"])dnl
AC_ARG_ENABLE(dbgassert,
	[  --enable-dbgassert      en/disable DBGASSERT macros (default is debug/opt)],
	[enable_dbgassert="$enableval"],
	[enable_dbgassert="default"])dnl
[
  if test "$with_debug" = "yes"; then
    with_debug="-g";
  fi

  if test "$lofar_compiler" = "gnu"; then
    lofar_warnflags="-W -Wall -Wno-unknown-pragmas";
  fi
# Suppress KCC warnings about returning by const value and about double ;
  if test "$lofar_compiler" = "kcc"; then
    lofar_warnflags="--display_error_number --restrict --diag_suppress 815,381";
  fi

  enable_debug="no";
  if test "$with_debug" != "no"; then
    enable_debug="yes";
  else
    if test "$with_optimize" = "no"; then
      enable_debug="yes";
    fi
  fi
  if test "$enable_debug" = "yes"; then]
AC_DEFINE(LOFAR_DEBUG,dnl
	1, [Define if we are compiling with debugging information])dnl
[ fi
  lfr_cppflags=
  lfr_clags=
  lfr_cxxflags=
  lfr_ldflags=
  if test "$enable_debug" != "no"; then
    lfr_cppflags="$lfr_cppflags -DUSE_DEBUG";
    lfr_cflags="$lfr_cflags -g";
    lfr_cxxflags="$lfr_cxxflags -g $lofar_warnflags";
    if test "$enable_tracer" = "default"; then
      enable_tracer="yes";
    fi
    if test "$enable_dbgassert" = "default"; then
      enable_dbgassert="yes";
    fi
  fi

  with_optimizecxx="$with_optimize";
  if test "$with_optimize" = "yes"; then
    with_optimize="-O3"
    if test "$lofar_compiler" = "kcc"; then
      with_optimizecxx="+K3"
    else
      with_optimizecxx="-O3"
    fi
  fi

  if test "$with_optimize" != "no"; then
    lfr_cflags="$lfr_cflags $with_optimize";
    lfr_cxxflags="$lfr_cxxflags $with_optimizecxx $lofar_warnflags";
    if test "$enable_tracer" = "default"; then
      enable_tracer="no";
    fi
    if test "$enable_dbgassert" = "default"; then
      enable_dbgassert="no";
    fi
  fi

  if test "$with_threads" != "no"; then
    lfr_cppflags="$lfr_cppflags -DUSE_THREADS -pthread";
    if test "$lofar_compiler" = "gnu"; then
      lfr_cppflags="$lfr_cppflags -D_GNU_SOURCE";
    fi
    lfr_ldflags="$lfr_ldflags -pthread";
  fi

  CPPFLAGS="$CPPFLAGS $lfr_cppflags $with_cppflags"
  CFLAGS="$lfr_cflags $with_cflags"
  CXXFLAGS="$lfr_cxxflags $with_cxxflags"
  LDFLAGS="$LDFLAGS $lfr_ldflags $with_ldflags"
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(CPPFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
[
  if test "$enable_tracer" != "no"; then]
    AC_DEFINE(ENABLE_TRACER,dnl
	1, [Define if TRACER is enabled])dnl
  [fi
  if test "$enable_dbgassert" != "no"; then]
    AC_DEFINE(ENABLE_DBGASSERT,dnl
	1, [Define if DbgAssert is enabled])dnl
  [fi

  if test "$with_debug" != "no"; then
    if test "$with_optimize" != "no"; then]
AC_MSG_ERROR([Can not have both --with-debug and --with-optimize])
[
    fi
  fi
]])dnl

#
# lofar_CHECK_PRETTY_FUNCTION
#
# If the C++ compiler supports the __PRETTY_FUNCTION__ macro,
#   define `HAVE_PRETTY_FUNCTION'
# else if compiler supports the __FUNCTION__ macro, 
#   define `HAVE_FUNCTION'
#
# Based on ICE and DDD autoconf macros; added test for __FUNCTION__.
#
AC_DEFUN([lofar_CHECK_PRETTY_FUNCTION],[
  AC_PREREQ(2.13)
  AC_REQUIRE([AC_PROG_CXX])
  AC_MSG_CHECKING(whether ${CXX} supports __PRETTY_FUNCTION__)
  AC_CACHE_VAL(lofar_cv_have_pretty_function,[
    AC_LANG_PUSH(C++)
    AC_TRY_LINK(
      [#include <stdio.h>],
      [puts(__PRETTY_FUNCTION__);],
      lofar_cv_have_pretty_function=yes,
      lofar_cv_have_pretty_function=no)
    AC_LANG_POP(C++)
  ])
  AC_MSG_RESULT($lofar_cv_have_pretty_function)
  if test "$lofar_cv_have_pretty_function" = yes; then
    AC_DEFINE(HAVE_PRETTY_FUNCTION,1,[Define if __PRETTY_FUNCTION__ is defined])
    echo "PRETTY_FUNCTION" >> pkgext;
  else
    AC_MSG_CHECKING(whether ${CXX} supports __FUNCTION__)
    AC_CACHE_VAL(lofar_cv_have_function,[
      AC_LANG_PUSH(C++)
      AC_TRY_LINK(
        [#include <stdio.h>],
        [puts(__FUNCTION__);],
        lofar_cv_have_function=yes,
        lofar_cv_have_function=no)
      AC_LANG_POP(C++)
    ])
    AC_MSG_RESULT($lofar_cv_have_function)
    if test "$lofar_cv_have_function" = yes; then
      AC_DEFINE(HAVE_FUNCTION,1,[Define if __FUNCTION__ is defined])
      echo "FUNCTION" >> pkgext;
    fi
  fi
])

#
# lofar_CHECK_LONG_LONG
#
# If the C++ compiler supports `long long' types,  define `HAVE_LONG_LONG'.
#
# Based on ICE and DDD autoconf macros.
#
AC_DEFUN([lofar_CHECK_LONG_LONG],[
  AC_PREREQ(2.13)
  AC_REQUIRE([AC_PROG_CXX])
  AC_MSG_CHECKING(whether ${CXX} supports long long)
  AC_CACHE_VAL(lofar_cv_have_long_long,[
    AC_LANG_PUSH(C++)
    AC_TRY_COMPILE(,[long long a;], 
      lofar_cv_have_long_long=yes, 
      lofar_cv_have_long_long=no)
    AC_LANG_POP(C++)
  ])
  AC_MSG_RESULT($lofar_cv_have_long_long)
  if test "$lofar_cv_have_long_long" = yes; then
    AC_DEFINE(HAVE_LONG_LONG,1,[Define if `long long' is supported])
  fi
  echo "LONG_LONG" >> pkgext;
])
