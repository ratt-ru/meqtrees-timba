#  lofar_blitz.m4
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


# lofar_BLITZ
#
# Macro to check for BLITZ installation
#
# lofar_BLITZ(option, [DEFAULT-PREFIX])
#     option 0 means that Blitz++ is optional, otherwise mandatory.
#
# e.g. lofar_BLITZ(["/usr/local/blitz"])
# -------------------------
#
AC_DEFUN(lofar_BLITZ,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], [lfr_option=0], [lfr_option=$1])
ifelse($2, [], define(DEFAULT_BLITZ_PREFIX,[/usr/local]), define(DEFAULT_BLITZ_PREFIX,$2))
AC_ARG_WITH(blitz,
	[  --with-blitz[=PFX]     prefix where Blitz is installed (default=]DEFAULT_BLITZ_PREFIX[)],
	[with_blitz=$withval],
	[with_blitz=""])
AC_ARG_WITH(blitz-libdir,
	[  --with-blitz-libdir=PFX   prefix where Blitz library is installed],
	[with_blitzdir=$withval],
	[with_blitzdir=""])
[
enable_blitz=no
if test "$lfr_option" = "1"; then
  enable_blitz=yes
fi
if test "$with_blitz" != "no"; then
  if test "$with_blitz" = ""; then
    blitz_prefix=]DEFAULT_BLITZ_PREFIX[
    if test "$with_blitzdir" != ""; then
      enable_blitz=yes
    fi
  else
    if test "$with_blitz" = "yes"; then
      blitz_prefix=]DEFAULT_BLITZ_PREFIX[
    else
      blitz_prefix=$withval
    fi
    enable_blitz=yes
  fi
]
##
## Look for header file in suggested location or in its include subdir
##
  AC_CHECK_FILE([$blitz_prefix/blitz/array.h],
			[lfr_header_blitz=$blitz_prefix/blitz],
			[lfr_header_blitz=no])dnl
[
  if test "$lfr_header_blitz" != "no" ; then
    if test "$with_blitzdir" = ""; then
      with_blitzdir=$blitz_prefix/blitz/lib
    fi
  else
]
    AC_CHECK_FILE([$blitz_prefix/include/blitz/array.h],
			[lfr_header_blitz=$blitz_prefix/include],
			[lfr_lib_blitz=no])dnl
[
    if test "$lfr_header_blitz" != "no"; then
      if test "$with_blitzdir" = ""; then
        with_blitzdir=$blitz_prefix/lib
      fi
    fi
  fi
  if test "$with_blitzdir" != ""; then
]
    AC_CHECK_FILE([$with_blitzdir/libblitz.a],
			[lfr_lib_blitz=$with_blitzdir],
			[lfr_lib_blitz=no])dnl
[
  fi

  if test "$lfr_header_blitz" != "no"  -a  "$lfr_lib_blitz" != "no" ; then
    BLITZ_CPPFLAGS="-I$lfr_header_blitz"
    BLITZ_CXXFLAGS=
    if test "$lofar_compiler" = "gnu"; then
      BLITZ_CXXFLAGS="-Wno-unused -ftemplate-depth-30"
    fi
    BLITZ_LDFLAGS="-L$lfr_lib_blitz"
    BLITZ_LIBS="-lblitz -lm"

    CPPFLAGS="$CPPFLAGS $BLITZ_CPPFLAGS"
    CXXFLAGS="$CXXFLAGS $BLITZ_CXXFLAGS"
    LDFLAGS="$LDFLAGS $BLITZ_LDFLAGS"
    LIBS="$LIBS $BLITZ_LIBS"
]
dnl
    AC_SUBST(CPPFLAGS)dnl
    AC_SUBST(CXXFLAGS)dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
dnl
    AC_DEFINE(HAVE_BLITZ, 1, [Define if Blitz is installed])dnl
[
  else
    if test "$enable_blitz" = "yes" ; then
]
      AC_MSG_ERROR([Could not find Blitz headers or library in $blitz_prefix])
[
    fi
    enable_blitz=no
  fi
fi]
AM_CONDITIONAL(HAVE_BLITZ, [test "$enable_blitz" = "yes"])
])
