#  lofar_external.m4
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


# lofar_EXTERNAL
#
# Macro to check for installation of external packages (e.g. FFTW)
#
# lofar_EXTERNAL(package, [option], headerfile, [libraries], [searchpath])
#     package is the name of the external package (e.g. BLITZ)
#     option 0 means that package is optional, otherwise mandatory.
#         default option=0
#     headerfile is the header file to be looked for
#     libraries are the package libraries to be looked for and to be
#         added to the LD command
#         separate by blanks if multiple libraries
#         default is package name in lowercase
#     searchpath is the path to look for header files and libraries
#         the path must be separated by blanks
#         +pkg is a special name; it is replaced by the package name.
#         +comp is a special name; it is replaced by the compiler name.
#         default is "/usr/local/+pkg/+comp /usr/local/+pkg /usr/local /usr"
#
# Extra libraries can be given via the with-'package'-extra-libs
# configure option.
# Similarly, extra LD, CXX, or CPP flags can be given via
#  with-'package'-extra-ld, -cxx, -cpp.
#
# For example:
#  lofar_EXTERNAL (blitz,1,blitz/blitz.h)
#    configures the blitz package.
#    When compiling with gnu3, the default search path is
#      /usr/local/blitz/gnu3 /usr/local/blitz/gnu /usr/local/blitz
#      /usr/local /usr
#
# -------------------------
#
AC_DEFUN(lofar_EXTERNAL,dnl
[dnl
AC_PREREQ(2.13)dnl
define(LOFAR_EXT_SYM,m4_toupper(m4_patsubst([$1], [.*/])))
define(LOFAR_EXT_LIB,m4_tolower(m4_patsubst([$1], [.*/])))
ifelse($2, [], [lfr_option=0], [lfr_option=$2])
ifelse($3, [], [lfr_hdr=""], [lfr_hdr=$3])
ifelse($4, [], [lfr_libs=LOFAR_EXT_LIB], [lfr_libs=$4])
ifelse($5, [], [lfr_search="/usr/local/+pkg/+comp /usr/local/+pkg /usr/local /usr"], [lfr_search=$5])
AC_ARG_WITH([LOFAR_EXT_LIB],
	[  --with-LOFAR_EXT_LIB[[=PFX]]        path to $1 directory],
	[with_external=$withval
         if test "${with_external}" = yes; then
            with_external=
         fi],
	[with_external=])

AC_ARG_WITH([LOFAR_EXT_LIB][[-libdir]],
  [  --with-LOFAR_EXT_LIB[-libdir]=PFX   specific library dir for $1 library],
  [lfr_external_libdir="$withval"],
  [lfr_external_libdir=])

AC_ARG_WITH([LOFAR_EXT_LIB][[-extra-libs]],
  [  --with-LOFAR_EXT_LIB[-extra-libs]   extra libraries for $1 (e.g. -lm)],
  [lfr_extra_libs="$withval"],
  [lfr_extra_libs=""])

AC_ARG_WITH([LOFAR_EXT_LIB][[-extra-ld]],
  [  --with-LOFAR_EXT_LIB[-extra-ld]     extra LD arguments for $1],
  [lfr_extra_ld="$withval"],
  [lfr_extra_ld=""])

AC_ARG_WITH([LOFAR_EXT_LIB][[-extra-cxx]],
  [  --with-LOFAR_EXT_LIB[-extra-cxx]    extra CXX arguments for $1],
  [lfr_extra_cxx="$withval"],
  [lfr_extra_cxx=""])

AC_ARG_WITH([LOFAR_EXT_LIB][[-extra-cpp]],
  [  --with-LOFAR_EXT_LIB[-extra-cpp]    extra CPP arguments for $1],
  [lfr_extra_cpp="$withval"],
  [lfr_extra_cpp=""])

[
##
## Blank extra stuff if yes or no is given.
##
if test "lfr_extra_libs" = "yes"  -o  "lfr_extra_libs" = "no"; then
  lfr_extra_libs=""
fi
if test "lfr_extra_ld" = "yes"  -o  "lfr_extra_ld" = "no"; then
  lfr_extra_ld=""
fi
if test "lfr_extra_cxx" = "yes"  -o  "lfr_extra_cxx" = "no"; then
  lfr_extra_cxx=""
fi
if test "lfr_extra_cpp" = "yes"  -o  "lfr_extra_cpp" = "no"; then
  lfr_extra_cpp=""
fi
##
## Look if an external package is used.
## It is if mandatory or if given by user.
## Also determine the given search path.
##
lfr_ext_name=]LOFAR_EXT_LIB[
enable_external=no
if test "$lfr_option" = "1"; then
  enable_external=yes
fi
if test "$with_external" = "no"; then
  if test "$enable_external" = "yes"; then
]
    AC_MSG_ERROR(--with-LOFAR_EXT_LIB=no cannot be given; LOFAR_EXT_SYM package is mandatory)
[
  fi
else
  if test "$with_external" = ""; then
    external_search=
    if test "$with_external_libdir" != ""; then
      enable_external=yes
    fi
  else
    if test "$with_external" = "yes"; then
      external_search=
    else
      external_search=$with_external
    fi
    enable_external=yes
  fi
##
## Replace +pkg and +comp in search list.
##
  external_slist=$external_search;
  if test "$external_slist" = ""; then
    external_slist="$lfr_search";
  fi
  if test "$external_slist" = ""; then
    external_slist="/usr/local /usr";
  fi
  lfr_slist=
  lfr_buildcomp=`echo $lofar_variant | sed -e "s/_.*//"`
  for bdir in $external_slist
  do
    lfr_a=`echo $bdir | sed -e "s%/+pkg%/$lfr_ext_name%g"`
    lfr_b=`echo $lfr_a | sed -e "s%/+comp%/$lfr_buildcomp%"`
    lfr_slist="$lfr_slist $lfr_b"
    if test "$lfr_a" != "$lfr_b"; then
      if test "$lfr_buildcomp" != "$lofar_compiler"; then
        lfr_b=`echo $lfr_a | sed -e "s%/+comp%/$lofar_compiler%"`
        lfr_slist="$lfr_slist $lfr_b"
      fi
    fi
  done

## Look for the header file in include directories of the search list.
  for bdir in $lfr_slist
  do
    ]AC_CHECK_FILE([$bdir/include/$lfr_hdr],
			[lfr_ext_inc=$bdir/include],
			[lfr_ext_inc=no])[
    if test "$lfr_ext_inc" != "no" ; then
      if test "$lfr_external_libdir" = ""; then
        lfr_external_libdir=$bdir/lib;
        break;
      fi
    fi
  done

  if test "$lfr_external_libdir" != ""; then
    lfr_ext_lib=
    for lib in $lfr_libs
    do
      if test "$lfr_ext_lib" != "no" ; then
        ]AC_CHECK_FILE([$lfr_external_libdir/lib$lib.a],
			[lfr_ext_lib=$lfr_external_libdir],
			[lfr_ext_lib=no])[
      fi
    done
  fi

  if test "$lfr_ext_inc" != "no"  -a  "$lfr_ext_lib" != "no" ; then
    EXTERNAL_CPPFLAGS="-I$lfr_ext_inc"
    EXTERNAL_LDFLAGS="-L$lfr_ext_lib"
    EXTERNAL_LIBS=
    for lib in $lfr_libs
    do
      EXTERNAL_LIBS="$EXTERNAL_LIBS -l$lib"
    done

    CPPFLAGS="$CPPFLAGS $EXTERNAL_CPPFLAGS $lfr_extra_cpp"
    CXXFLAGS="$CXXFLAGS $lfr_extra_cxx"
    LDFLAGS="$LDFLAGS $EXTERNAL_LDFLAGS $lfr_extra_ld"
    LIBS="$LIBS $EXTERNAL_LIBS $lfr_extra_libs"
]
dnl
    AC_SUBST(CPPFLAGS)dnl
    AC_SUBST(CXXFLAGS)dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
dnl
    AC_DEFINE([HAVE_]LOFAR_EXT_SYM, 1, [Define if ]LOFAR_EXT_SYM[ is installed])dnl
[
  else
    if test "$enable_external" = "yes" ; then
]
      AC_MSG_ERROR([Could not find ]LOFAR_EXT_SYM[ headers or library in $lfr_slist])
[
    fi
    enable_external=no
  fi
fi]
AM_CONDITIONAL([HAVE_]LOFAR_EXT_SYM, [test "$enable_external" = "yes"])
])
