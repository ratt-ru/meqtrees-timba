#  lofar_fftw.m4
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


# lofar_FFTW
#
# Macro to check for FFTW and RFFTW installation
#
# lofar_FFTW(option, [DEFAULT-PREFIX])
#     option 0 means that FFTW is optional, otherwise mandatory.
#
# e.g. lofar_FFTW(1)
# -------------------------
#
AC_DEFUN(lofar_FFTW,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], [lfr_option=0], [lfr_option=$1])
AC_ARG_WITH(fftw,
	[  --with-fftw[=PFX]     prefix where FFTW is installed (default=]DEFAULT_FFTW_PREFIX[)],
	[with_fftw=$withval],
	[with_fftw=""])
AC_ARG_WITH(fftw-libdir,
	[  --with-fftw-libdir=PFX   prefix where FFTW library is installed],
	[with_fftw_libdir=$withval],
	[with_fftw_libdir=""])
[
enable_fftw=no
if test "$lfr_option" = "1"; then
  enable_fftw=yes
fi
if test "$with_fftw" != "no"; then
  if test "$with_fftw" = ""; then
    fftw_prefix=
    if test "$with_fftw_libdir" != ""; then
      enable_fftw=yes
    fi
  else
    if test "$with_fftw" = "yes"; then
      fftw_prefix=
    else
      fftw_prefix=$with_fftw
    fi
    enable_fftw=yes
  fi
##
## Look for header file in suggested locations or in its include subdir
##
  fftw_inclist=$fftw_prefix;
  if test "$fftw_prefix" = ""; then
    fftw_inclist=
    lfr_buildcomp=`echo $lofar_variant | sed -e "s/_.*//"`
    if test "$lfr_buildcomp" != ""; then
      fftw_inclist="/usr/local/fftw/$lfr_buildcomp";
    fi
    if test "$lfr_buildcomp" != "$lofar_compiler"; then
      fftw_inclist="$fftw_inclist /usr/local/fftw/$lofar_compiler";
    fi
    fftw_inclist="$fftw_inclist /usr/local";
  fi
  for bdir in $fftw_inclist
  do
    ]AC_CHECK_FILE([$bdir/include/fftw.h],
			[lfr_header_fftw=$bdir/include],
			[lfr_header_fftw=no])[
    if test "$lfr_header_fftw" != "no" ; then
      ]AC_CHECK_FILE([$bdir/include/rfftw.h],
			[lfr_header_fftw=$bdir/include],
			[lfr_header_fftw=no])[
      if test "$lfr_header_fftw" != "no" ; then
        if test "$with_fftw_libdir" = ""; then
          with_fftw_libdir=$bdir/lib;
          break;
        fi
      fi
    fi
  done

  if test "$with_fftw_libdir" != ""; then
    ]AC_CHECK_FILE([$with_fftw_libdir/libfftw.a],
			[lfr_lib_fftw=$with_fftw_libdir],
			[lfr_lib_fftw=no])[
    if test "$lfr_lib_fftw" != "no" ; then
      ]AC_CHECK_FILE([$with_fftw_libdir/include/fftw.h],
			[lfr_lib_fftw=$with_fftw_libdir],
			[lfr_lib_fftw=no])[
    fi
  fi

  if test "$lfr_header_fftw" != "no"  -a  "$lfr_lib_fftw" != "no" ; then
    FFTW_CPPFLAGS="-I$lfr_header_fftw"
    FFTW_CXXFLAGS=
    if test "$lofar_compiler" = "gnu"; then
      FFTW_CXXFLAGS="-Wno-unused -ftemplate-depth-30"
    fi
    FFTW_LDFLAGS="-L$lfr_lib_fftw"
    FFTW_LIBS="-lfftw -lm"

    CPPFLAGS="$CPPFLAGS $FFTW_CPPFLAGS"
    CXXFLAGS="$CXXFLAGS $FFTW_CXXFLAGS"
    LDFLAGS="$LDFLAGS $FFTW_LDFLAGS"
    LIBS="$LIBS $FFTW_LIBS"
]
dnl
    AC_SUBST(CPPFLAGS)dnl
    AC_SUBST(CXXFLAGS)dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
dnl
    AC_DEFINE(HAVE_FFTW, 1, [Define if FFTW is installed])dnl
[
  else
    if test "$enable_fftw" = "yes" ; then
]
      AC_MSG_ERROR([Could not find FFTW headers or library in $fftw_prefix])
[
    fi
    enable_fftw=no
  fi
fi]
AM_CONDITIONAL(HAVE_FFTW, [test "$enable_fftw" = "yes"])
])
