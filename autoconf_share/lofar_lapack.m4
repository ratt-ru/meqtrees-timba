#  lofar_lapack.m4
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


# lofar_LAPACK
#
# Macro to check for LAPACK and BLAS installation
#
# lofar_LAPACK(option, [DEFAULT-PREFIX])
#     option 0 means that LAPACK is optional, otherwise mandatory.
#
# e.g. lofar_LAPACK(1)
# --------------------
#
AC_DEFUN([lofar_LAPACK],dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], [lfr_option=0], [lfr_option=$1])
AC_ARG_WITH(lapack,
	[  --with-lapack[=PFX]     prefix where lapack/blas library are installed],
	[with_lapack=$withval],
	[with_lapack=""])
[
enable_lapack=no
if test "$lfr_option" = "1"; then
  enable_lapack=yes
fi
if test "$with_lapack" != "no"; then
  if test "$with_lapack" = ""; then
    lapack_prefix=
  else
    if test "$with_lapack" = "yes"; then
      lapack_prefix=
    else
      lapack_prefix=$with_lapack
    fi
    enable_lapack=yes
  fi
##
## Look for library in suggested locations or in its lib subdir
##
  lapack_inclist=$lapack_prefix;
  if test "$lapack_prefix" = ""; then
    lapack_inclist=
    lfr_buildcomp=`echo $lofar_variant | sed -e "s/_.*//"`
    if test "$lfr_buildcomp" != ""; then
      lapack_inclist="/usr/local/lapack/$lfr_buildcomp";
    fi
    if test "$lfr_buildcomp" != "$lofar_compiler"; then
      lapack_inclist="$lapack_inclist /usr/local/lapack/$lofar_compiler";
    fi
    lapack_inclist="$lapack_inclist /usr/local";
  fi
  for bdir in $lapack_inclist
  do
    ]AC_CHECK_FILE([$bdir/lib/liblapack.a],
			[lfr_lib_lapack=$bdir/lib],
			[lfr_lib_lapack=no])[
  done

  if test "$lfr_lib_lapack" != "no"; then
    ]AC_CHECK_FILE([$lfr_lib_lapack/libblas.a],
			[lfr_lib_blas=$lfr_lin_lapack/libblas.a],
			[lfr_lib_blas=no])[
  fi

  if test "$lfr_lib_lapack" != "no"  -a  "$lfr_lib_blas" != "no" ; then
    LAPACK_LDFLAGS="-L$lfr_lib_lapack"
    LAPACK_LIBS="-llapack -lblas -lg2c"

    LDFLAGS="$LDFLAGS $LAPACK_LDFLAGS"
    LIBS="$LIBS $LAPACK_LIBS"
]
dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
dnl
    AC_DEFINE(HAVE_LAPACK, 1, [Define if lapack is installed])dnl
[
  else
    if test "$enable_lapack" = "yes" ; then
]
      AC_MSG_ERROR([Could not find lapack or blas library in $lapack_prefix])
[
    fi
    enable_lapack=no
  fi
fi]
AM_CONDITIONAL(HAVE_LAPACK, [test "$enable_lapack" = "yes"])
])
