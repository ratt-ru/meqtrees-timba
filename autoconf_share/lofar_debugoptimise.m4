#  lofar_debugoptimise.m4
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


# lofar_DEBUG_OPTIMIZE
#
# Set debugging or optimisation flags for CC and CXX
#
AC_DEFUN(lofar_DEBUG_OPTIMIZE,dnl
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
	[  --disable-tracer        disable TRACER macros],
	[enable_tracer="$enableval"],
	[enable_tracer=yes])dnl
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
  if test "$enable_debug" != "no"; then
    lfr_cflags="-g";
    lfr_cxxflags="-g $lofar_warnflags";
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
    lfr_cflags="$with_optimize";
    lfr_cxxflags="$with_optimizecxx $lofar_warnflags";
    if test "$enable_dbgassert" = "default"; then
      enable_dbgassert="no";
    fi
  fi

  CPPFLAGS="$CPPFLAGS $with_cppflags"
  CFLAGS="$lfr_cflags $with_cflags"
  CXXFLAGS="$lfr_cxxflags $with_cxxflags"
  LDFLAGS="$LDFLAGS $with_ldflags"
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
