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
# lofar_BLITZ(option)
#     option 0 means that Blitz++ is optional, otherwise mandatory.
#
# e.g. lofar_BLITZ(1)
# -------------------------
#
AC_DEFUN(lofar_BLITZ,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], [lfr_option=0], [lfr_option=$1])
AC_ARG_WITH(blitz,
	[  --with-blitz[=PFX]     prefix where Blitz is installed (default=/usr/local)],
	[with_blitz=$withval],
	[with_blitz=""])
AC_ARG_WITH(blitz-libdir,
	[  --with-blitz-libdir=PFX   prefix where Blitz library is installed],
	[with_blitz_libdir=$withval],
	[with_blitz_libdir=""])
[
enable_blitz=no
if test "$lfr_option" = "1"; then
  enable_blitz=yes
fi
if test "$with_blitz" != "no"; then
  if test "$with_blitz" = ""; then
    blitz_prefix=
    if test "$with_blitz_libdir" != ""; then
      enable_blitz=yes
    fi
  else
    if test "$with_blitz" = "yes"; then
      blitz_prefix=
    else
      blitz_prefix=$with_blitz
    fi
    enable_blitz=yes
  fi
##
## Look for header file in suggested locations or in its include subdir
##
  blitz_inclist=$blitz_prefix;
  if test "$blitz_prefix" = ""; then
    blitz_inclist=
    lfr_buildcomp=`echo $lofar_variant | sed -e "s/_.*//"`
    if test "$lfr_buildcomp" != ""; then
      blitz_inclist="/usr/local/blitz/$lfr_buildcomp";
    fi
    if test "$lfr_buildcomp" != "$lofar_compiler"; then
      blitz_inclist="$blitz_inclist /usr/local/blitz/$lofar_compiler";
    fi
    blitz_inclist="$blitz_inclist /usr/local";
  fi
  for bdir in $blitz_inclist
  do
    ]AC_CHECK_FILE([$bdir/include/blitz/array.h],
			[lfr_header_blitz=$bdir/include],
			[lfr_header_blitz=no])[
    if test "$lfr_header_blitz" != "no" ; then
      if test "$with_blitz_libdir" = ""; then
        with_blitz_libdir=$bdir/lib;
        break;
      fi
    fi
  done

  if test "$with_blitz_libdir" != ""; then
    ]AC_CHECK_FILE([$with_blitz_libdir/libblitz.a],
			[lfr_lib_blitz=$with_blitz_libdir],
			[lfr_lib_blitz=no])[
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
