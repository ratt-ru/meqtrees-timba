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
# lofar_EXTERNAL(package, [option], headerfile, [libraries], [searchpath].
#            [extra_cppflags],[extra_cxxflags],[extra_ldflags],[extra_libs]
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
#         +prefix is a special name; it is replaced by the --prefix value
#           which can be used to find a package in the install directory.
#         +pkg is a special name; it is replaced by the package name.
#         +comp is a special name; it is replaced by the compiler name.
#         +vers is a special name; it is replaced by the package version
#               which can be given as e.g.  --with-python-version=2.2
#         default is
#          "+prefix /usr/local/+pkg+vers/+comp /usr/local/+pkg+vers
#           /usr/local /usr"
#         The header and libraries are looked up in each directory of the
#         search path and in include/lib subdirectories of them.
#         The first match is taken.
#         Note that at configure time the user can specify the directory
#         for header and library which overrides the searchpath.
#     extra_cppflags, extra_cxxflags, extra_ldflags, and extra_libs
#         are extra options for the preprocessor, compiler, and linker.
#         It is a blank separated list of options. An option can be preceeded
#         by the compiler type and a colon indicating that the flag should
#         only be used for that compiler.
#         E.g. gnu:-Wno-unused
#             could be used for the blitz package to avoid too many warnings.
#         
#
# For example:
#  lofar_EXTERNAL (blitz,1,blitz/blitz.h,,,,"gnu:-Wno-unused",,-lm)
#    configures the blitz package.
#    When compiling with gnu3, the default search path is
#      /usr/local/blitz/gnu3 /usr/local/blitz/gnu /usr/local/blitz
#      /usr/local /usr
#
# -------------------------
#
AC_DEFUN([lofar_EXTERNAL],dnl
[dnl
AC_PREREQ(2.13)dnl
define(LOFAR_EXT_SYM,m4_toupper(patsubst([$1], [.*/])))
define(LOFAR_EXT_LIB,m4_tolower(patsubst([$1], [.*/])))
ifelse($2, [], [lfr_option=0], [lfr_option=$2])
ifelse($3, [], [lfr_hdr=""], [lfr_hdr=$3])
ifelse($4, [], [lfr_libs=LOFAR_EXT_LIB], [lfr_libs=$4])
ifelse($5, [], [lfr_search="+prefix /usr/local/+pkg+vers/+comp /usr/local/+pkg+vers /usr/local /usr"], [lfr_search=$5])
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

AC_ARG_WITH([LOFAR_EXT_LIB][[-version]],
  [  --with-LOFAR_EXT_LIB[-version]=PFX  specific version for $1],
  [lfr_ext_version="$withval"],
  [lfr_ext_version=])

[
##
## Set version to blank if it is yes or no.
##
if test "$lfr_ext_version" = "no"  -o  "$lfr_ext_version" = "yes"; then
  lfr_ext_version=;
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
## Get build compiler and type
##
  lfr_buildcomp=`echo $lofar_variant | sed -e "s/_.*//"`
  lfr_buildtype=`echo $lofar_variant | sed -e "s/.*_//"`
##
## Get the extra flags, possibly compiler dependent.
##
  lfr_cpp=$6
  lfr_cxx=$7
  lfr_ld=$8
  lfr_lb=$9

  lfr_extra_cpp=
  for flag in $lfr_cpp
  do
    flagv=`echo $flag | sed -e "s/.*://"`
    flagc=`echo $flag | sed -e "s/:.*//"`
    if [ "$flagc" = "$flagv" ]; then
      flagc="";
    fi
    flagcc=`echo $flagc | sed -e "s/_.*//"`
    flagct=`echo $flagc | sed -e "s/.*_//"`
    if [ "$flagct" = "$flagcc" ]; then
      flagct="";
    fi
    if [ "$flagcc" = "" -o "$flagcc" = "$lfr_buildcomp" ]; then
      if [ "$flagct" = "" -o "$flagct" = "$lfr_buildtype" ]; then
        lfr_extra_cpp="$lfr_extra_cpp $flagv";
      fi
    fi
  done

  lfr_extra_cxx=
  for flag in $lfr_cxx
  do
    flagv=`echo $flag | sed -e "s/.*://"`
    flagc=`echo $flag | sed -e "s/:.*//"`
    if [ "$flagc" = "$flagv" ]; then
      flagc="";
    fi
    flagcc=`echo $flagc | sed -e "s/_.*//"`
    flagct=`echo $flagc | sed -e "s/.*_//"`
    if [ "$flagct" = "$flagcc" ]; then
      flagct="";
    fi
    if [ "$flagcc" = "" -o "$flagcc" = "$lfr_buildcomp" ]; then
      if [ "$flagct" = "" -o "$flagct" = "$lfr_buildtype" ]; then
        lfr_extra_cxx="$lfr_extra_cxx $flagv";
      fi
    fi
  done

  lfr_extra_ld=
  for flag in $lfr_ld
  do
    flagv=`echo $flag | sed -e "s/.*://"`
    flagc=`echo $flag | sed -e "s/:.*//"`
    if [ "$flagc" = "$flagv" ]; then
      flagc="";
    fi
    flagcc=`echo $flagc | sed -e "s/_.*//"`
    flagct=`echo $flagc | sed -e "s/.*_//"`
    if [ "$flagct" = "$flagcc" ]; then
      flagct="";
    fi
    if [ "$flagcc" = "" -o "$flagcc" = "$lfr_buildcomp" ]; then
      if [ "$flagct" = "" -o "$flagct" = "$lfr_buildtype" ]; then
        lfr_extra_ld="$lfr_extra_ld $flagv";
      fi
    fi
  done

  lfr_extra_libs=
  for flag in $lfr_lb
  do
    flagv=`echo $flag | sed -e "s/.*://"`
    flagc=`echo $flag | sed -e "s/:.*//"`
    if [ "$flagc" = "$flagv" ]; then
      flagc="";
    fi
    flagcc=`echo $flagc | sed -e "s/_.*//"`
    flagct=`echo $flagc | sed -e "s/.*_//"`
    if [ "$flagct" = "$flagcc" ]; then
      flagct="";
    fi
    if [ "$flagcc" = "" -o "$flagcc" = "$lfr_buildcomp" ]; then
      if [ "$flagct" = "" -o "$flagct" = "$lfr_buildtype" ]; then
        lfr_extra_libs="$lfr_extra_libs $flagv";
      fi
    fi
  done

##
## Replace +prefix, +pkg, +vers and +comp in search list.
##
  external_slist=$external_search;
  if test "$external_slist" = ""; then
    external_slist="$lfr_search";
  fi
  if test "$external_slist" = ""; then
    external_slist="/usr/local /usr";
  fi
  lfr_slist=
  for bdir in $external_slist
  do
    lfr_a0=`echo $bdir | sed -e "s%+prefix%$prefix%g"`
    lfr_a1=`echo $lfr_a0 | sed -e "s%+pkg%$lfr_ext_name%g"`
    lfr_a=`echo $lfr_a1 | sed -e "s%+vers%$lfr_ext_version%g"`
    lfr_b=`echo $lfr_a | sed -e "s%+comp%$lfr_buildcomp%"`
    lfr_slist="$lfr_slist $lfr_b"
    if test "$lfr_a" != "$lfr_b"; then
      if test "$lfr_buildcomp" != "$lofar_compiler"; then
        lfr_b=`echo $lfr_a | sed -e "s%+comp%$lofar_compiler%"`
        lfr_slist="$lfr_slist $lfr_b"
      fi
    fi
  done

## Look for the header file in directories of the search list
## and in its include subdirectories.
## Assume that libraries are in similar directory structure as headers.
## (thus in lib subdirectory if header is in include subdirectory)
  for bdir in $lfr_slist
  do
    ]AC_CHECK_FILE([$bdir/include/$lfr_hdr],
			[lfr_ext_inc=$bdir/include],
			[lfr_ext_inc=no])[
    if test "$lfr_ext_inc" != "no" ; then
      if test "$lfr_external_libdir" = ""; then
	if test "`arch`" = "x86_64"; then
          lfr_external_libdir=$bdir/lib64;
	else
          lfr_external_libdir=$bdir/lib;
	fi
      fi
      break;
    fi
    ]AC_CHECK_FILE([$bdir/$lfr_hdr],
			[lfr_ext_inc=$bdir],
			[lfr_ext_inc=no])[
    if test "$lfr_ext_inc" != "no" ; then
      if test "$lfr_external_libdir" = ""; then
        lfr_external_libdir=$bdir;
      fi
      break;
    fi
  done

  lfr_depend=
  if test "$lfr_external_libdir" != ""; then
    lfr_ext_lib=
    lfr_libsc=`echo $lfr_libs | sed -e "s%+vers%$lfr_ext_version%g"`
    for lib in $lfr_libsc
    do
      if test "$lfr_ext_lib" != "no" ; then
        ]AC_CHECK_FILE([$lfr_external_libdir/lib$lib.so],
			[lfr_ext_lib=$lfr_external_libdir],
			[lfr_ext_lib=no])[
        if test "$lfr_ext_lib" == "no" ; then
          ]AC_CHECK_FILE([$lfr_external_libdir/lib$lib.a],
			[lfr_ext_lib=$lfr_external_libdir],
			[lfr_ext_lib=no])[
          lfr_depend="$lfr_depend $lfr_external_libdir/lib$lib.a"
        else
          lfr_depend="$lfr_depend $lfr_external_libdir/lib$lib.so"
        fi
      fi
    done
  fi

  if test "$lfr_ext_inc" != "no"  -a  "$lfr_ext_lib" != "no" ; then
    EXTERNAL_CPPFLAGS=
    EXTERNAL_CXXFLAGS=
    EXTERNAL_LDFLAGS=
    EXTERNAL_LIBS=
    if test "$lfr_ext_inc" != "/usr/include" -a \
            "$lfr_ext_inc" != "/usr/local/include" ; then
      EXTERNAL_CPPFLAGS="-I$lfr_ext_inc"
    fi
    if test "$lfr_ext_lib" != "" ; then
      EXTERNAL_LDFLAGS="-L$lfr_ext_lib -Wl,-rpath,$lfr_ext_lib"
    fi
    for lib in $lfr_libsc
    do
      EXTERNAL_LIBS="$EXTERNAL_LIBS -l$lib"
    done

    EXTERNAL_CPPFLAGS="$EXTERNAL_CPPFLAGS $lfr_extra_cpp"
    EXTERNAL_CXXFLAGS="$EXTERNAL_CXXFLAGS $lfr_extra_cxx"
    EXTERNAL_LDFLAGS="$EXTERNAL_LDFLAGS $lfr_extra_ld"
    EXTERNAL_LIBS="$EXTERNAL_LIBS $lfr_extra_libs"

    echo ]LOFAR_EXT_SYM[ >> pkgext
    echo "$EXTERNAL_CPPFLAGS" >> pkgextcppflags
    echo "$EXTERNAL_CXXFLAGS" >> pkgextcxxflags

    CPPFLAGS="$CPPFLAGS $EXTERNAL_CPPFLAGS"
    CXXFLAGS="$CXXFLAGS $EXTERNAL_CXXFLAGS"
    LDFLAGS="$LDFLAGS $EXTERNAL_LDFLAGS"
    LIBS="$LIBS $EXTERNAL_LIBS"
    LOFAR_DEPEND="$LOFAR_DEPEND $lfr_depend"

    enable_external=yes
]
dnl
    AC_SUBST(CPPFLAGS)dnl
    AC_SUBST(CXXFLAGS)dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
    AC_SUBST(LOFAR_DEPEND)dnl
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
