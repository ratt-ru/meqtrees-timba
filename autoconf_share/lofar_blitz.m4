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
# lofar_BLITZ([DEFAULT-PREFIX])
#
# e.g. lofar_BLITZ(["/usr/local/blitz"])
# -------------------------
#
AC_DEFUN(lofar_BLITZ,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_BLITZ_PREFIX,[/usr/local/blitz]), define(DEFAULT_BLITZ_PREFIX,$1))
AC_ARG_WITH(blitz,
	[  --with-blitz[=PFX]     prefix where Blitz is installed (default=]DEFAULT_BLITZ_PREFIX[)],
	[with_blitz=$withval],
	[with_blitz="no"])
[
if test "$with_blitz" = "no"; then
  enable_blitz=no
else
  if test "$with_blitz" = "yes"; then
    blitz_prefix=]DEFAULT_BLITZ_PREFIX
[
  else
    blitz_prefix=$withval
  fi
  enable_blitz=yes
]
##
## Check in normal location and suggested location
##
AC_CHECK_FILE([$blitz_prefix/blitz/array.h],
			[lofar_cv_header_blitz=yes],
			[lofar_cv_header_blitz=no])dnl
[
  if test $lofar_cv_header_blitz = yes ; then

    BLITZ_PATH="$blitz_prefix"

    BLITZ_CPPFLAGS="-I$BLITZ_PATH"
    BLITZ_CXXFLAGS=
    if test "$lofar_compiler" = "gnu"; then
      BLITZ_CXXFLAGS="-Wno-unused -ftemplate-depth-30"
    fi
    BLITZ_LDFLAGS="-L$BLITZ_PATH/lib"
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
  else]
AC_MSG_ERROR([Could not find Blitz in $blitz_prefix])
[
    enable_blitz=no
  fi
fi]
AM_CONDITIONAL(HAVE_BLITZ, [test "$enable_blitz" = "yes"])
])
