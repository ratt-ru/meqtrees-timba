#  lofar_init.m4
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


# lofar_INIT
#
# Macro to initialize common LOFAR make variables and to
# define CXX if only CC is defined.
# It should be invoked before AC_PROG_CXX.
#
# It sets the following variables:
#  lofar_top_srcdir  user's LOFAR root (e.g. $HOME/sim/LOFAR)
#  lofar_sharedir    $lofar_top_srcdir/autoconf_share
#  lofar_root        LOFAR root which is default tree for package sources
#                    (e.g. /lofar/stable/LOFAR)
#  lofar_root_libdir LOFAR root which is default tree for package libraries
#                    It contains the string <package> which should be replaced
#                    by the actual package name.
#  lofar_use_root    0 = root is only a fallback
#                    1 = always use root (except for package to build)
#  lofar_variant     variant being built (e.g. gnu_opt or xxx)
#  lofar_compiler    compiler type used (gnu, kcc, or icc) derived from CXX
#                    Other compilers are not recognized and result in
#                    a warning.
#  LOFAR_DEPEND      all lofar libraries this package is dependent on
#
# A warning is given if the compiler type mismatches the compiler part
# of the variant.
#
# The configure option --with-lofar can be used to specify a particular
# version and/or variant.
# The version can be given as a path, where /home/lofar is added if only
# a version name like stable is given.
# Default version is stable.
# Default variant is the name of the variant being configured.
# E.g. if configuring BaseSim/build/gnu_debug
#   --with-lofar=weekly:opt   -> /lofar_weekly  gnu_opt
#   --with-lofar=:opt         -> /lofar/stable  gnu_opt
#   --with-lofar=~            -> $HOME          gnu_debug
#
# It is checked whether the version and variant exist.
#
#
AC_DEFUN(lofar_INIT,dnl
[dnl
AC_PREREQ(2.13)dnl
AC_ARG_WITH(lofar,
	[  --with-lofar[=version:variant]    root version:variant to use (default=user tree)],
	[with_lofar=$withval;
         lofar_use_root=1])

AC_ARG_WITH(lofar-default,
	[  --with-lofar-default[=version:variant]    root version:variant to use (default=user tree)],
	[with_lofar=$withval;
         lofar_use_root="${lofar_use_root}0"])

AC_ARG_WITH(lofar-libdir,
  [  --with-lofar-libdir=PFX   specific tree for lofar libraries],
  [lofar_root_libdir="$withval"])

[
  if test "$with_lofar" = yes; then
    with_lofar=
  fi
  if test "$lofar_use_root" = "10"; then
    ]AC_MSG_ERROR([--with-lofar and --with-lofar-default should not be used together])[
  fi
  if test "x$lofar_use_root" = "x"; then
    lofar_use_root=0;
  fi
  # Find root of user LOFAR directory tree.
  lfr_top=`(cd $srcdir && pwd) | sed -e "s%/LOFAR/.*%%"`
  lofar_top_srcdir=$lfr_top/LOFAR;
  lfr_pkg=`(cd $srcdir && pwd) | sed -e "s%$lofar_top_srcdir%%"`
  lfr_rest=`(echo $lfr_pkg) | sed -e "s%/LOFAR/.*%/LOFAR%"`
  if test "$lfr_pkg" != "$lfr_rest"; then
    ]AC_MSG_ERROR([Directory name LOFAR should be used only once in your path])[
  fi
  lofar_sharedir=$lofar_top_srcdir/autoconf_share
  # Determine if the build area has the compiler name in it
  # and get the root of the build tree.
  # The build area can be
  # like   something/build/variant/package  --> root = something/build/variant
  # or     something/package/build/variant  --> root = something
  lfr_curwd=`pwd`;
  lfr_curvar1=`pwd | sed -e "s%.*/build/%%"`;
  lfr_curvar=`echo $lfr_curvar1 | sed -e "s%/.*%%g"`;
  case "$lfr_curvar1" in
  */*)
    # root = something/build/variant
    lfr_curroot=`pwd | sed -e "s%/build/.*%/build/$lfr_curvar%"`;
    ;;
  *)
    # root = something
    # Strip the package name from the build path
    lfr_curroot=`pwd | sed -e "s%$lfr_pkg/.*%%"`
    ;;
  esac
  lfr_buildcomp=
  case "$lfr_curvar" in
  *_*)
    lfr_buildcomp=`echo $lfr_curvar | sed -e "s/_.*//"`
    ;;
  esac

  # If the C++ compiler is not given, set it to the C compiler (if given).
  if test "x$CXX" = "x"; then
    if test "x$CC" != "x"; then
      lfr_cxx=`basename $CC`;
      lfr_ccdir="";
      if test "x$lfr_cxx" != "x$CC"; then
        lfr_ccdir=`dirname $CC`/;
      elif test "x$lfr_cxx" = "xgcc"; then
        lfr_cxx="g++";
      fi
      CXX="$lfr_ccdir$lfr_cxx";
      ]AC_SUBST(CXX)[
    fi
  fi

  # Find the compiler type. Note that the default compiler is gnu g++.
  # Set the special AR needed for the KAI C++ compiler.
  lofar_compiler="gnu";
  if test "x$CXX" != "x"; then
    lfr_cxx=`basename $CXX`;
    if test "x$lfr_cxx" = "xg++"; then
      lofar_compiler="gnu";
    elif test "x$lfr_cxx" = "xKCC"; then
      lofar_compiler="kcc";
      AR="$CXX";
      AR_FLAGS="-o";
      ]AC_SUBST(AR)
       AC_SUBST(AR_FLAGS)[
    elif test "x$lfr_cxx" = "xicc"; then
      lofar_compiler="icc";
    else
      ]AC_MSG_WARN([$CXX is an unknown compiler for LOFAR; assuming gnu])[
    fi
  fi

  # Check if compiler matches build variant.
  if test "x$lfr_buildcomp" != "x"; then
    if test "x$lfr_buildcomp" != "x$lofar_compiler"; then
      ]AC_MSG_WARN([compiler $CXX mismatches build variant $lfr_curvar])[
    fi
  fi

  # Get the possible version:variant given.
  # Empty variant means the current variant.
  # Remove trailing / and /LOFAR if user has given that (redundantly).
  lofar_root=
  lofar_variant=
  if test "x$with_lofar" != "x"; then
    lofar_root=$with_lofar;
    case "$with_lofar" in
    *:*)
      lofar_root=`echo ${with_lofar} | sed -e "s/:.*//"`
      lofar_variant=`echo ${with_lofar} | sed -e "s/.*://"`
      ;;
    esac
    lofar_root=`echo $lofar_root | sed -e 's%/$%%' -e 's%/LOFAR$%%'`;
  fi
  # If root has no / or ~, add /home/lofar/ to it.
  # Replace ~ by home directory.
  # If variant has no _, add compiler_ to it.
  lfr_libdir=;
  if test "x$lofar_root" = "x"; then
    lofar_root=$lfr_top;
    lfr_libdir=$lfr_curroot;
  else
    case "$lofar_root" in
    ~*)
      lofar_root=`echo $lofar_root | sed -e "s%~%$HOME%"`;
      ;;
    */*)
      ;;
    ?*)
      lofar_root=/home/lofar/$lofar_root;
      ;;
    esac
  fi
  if test "x$lfr_libdir" = "x"; then
    lfr_libdir=$lofar_root/LOFAR;
  fi
  if test "x$lofar_root_libdir" = "x"; then
    lofar_root_libdir=$lfr_libdir;
  fi
  if test "x$lofar_variant" = "x"; then
    lofar_variant="$lfr_curvar";
  else
    case "$lofar_variant" in
    *_*)
      ;;
    *)
      lofar_variant=${lofar_compiler}_$lofar_variant;
      ;;
    esac
  fi

  # Create pkginc (used by lofar_package.m4) if not existing yet.
  # Create a symlink to the source directory of the package being configured.
  # Do the same for the build directory (for files creates from e.g. idl).
  if [ ! -d pkginc ]; then
    mkdir pkginc;
  fi
  lfr_srcdir=`cd $srcdir && pwd`;
  lfr_pkg=`basename $lfr_srcdir`;
  \rm -f pkginc/$lfr_pkg;
  ln -s $lfr_srcdir/src pkginc/$lfr_pkg;
  if [ ! -d pkgbldinc ]; then
    mkdir pkgbldinc;
  fi
  \rm -f pkgbldinc/$lfr_pkg;
  ln -s $lfr_curwd/src pkgbldinc/$lfr_pkg;

  # Create the lofar_config.h file.
  # Define a line for the package being configured.
  \rm -f lofar_config.h
  lfr_upkg=`echo $lfr_pkg | tr a-z A-Z`
  echo "#define HAVE_LOFAR_$lfr_upkg 1" > lofar_config.h

  CPPFLAGS="$CPPFLAGS -I$lfr_curwd/pkginc -I$lfr_curwd/pkgbldinc -I$lfr_curwd"
  LOFAR_DEPEND=
]
AC_CHECK_FILE([$lofar_root/LOFAR],
			[lfr_root=yes],
			[lfr_root=no])
  [if test $lfr_root = no; then]
    AC_MSG_WARN([Could not find LOFAR in $lofar_root])
  [fi
  lofar_root=$lofar_root/LOFAR

  case $lofar_root_libdir in
  */build/*)
    lfr_find=$lofar_root_libdir/LCS/Common;
    lofar_root_libdir="$lofar_root_libdir/<package>";
    ;;
  *)
    lfr_find=$lofar_root_libdir/LCS/Common/build/$lofar_variant;
    lofar_root_libdir="$lofar_root_libdir/<package>/build/$lofar_variant";
    ;;
  esac

]
AC_CHECK_FILE([$lfr_find], [lfr_var=yes], [lfr_var=no])
  [if test $lfr_var = no; then]
    AC_MSG_WARN([Could not find libdir $lfr_find]);
    [
    lofar_root_libdir="/home/lofar/stable/LOFAR/<package>/build/${lofar_compiler}_opt";
    ]
    AC_MSG_WARN([   set to /home/lofar/stable/LOFAR/${lofar_compiler}_opt])
  [fi]


  AC_SUBST(lofar_root)
  AC_SUBST(lofar_root_libdir)
  AC_SUBST(lofar_use_root)
  AC_SUBST(lofar_compiler)
  AC_SUBST(lofar_variant)
  AC_SUBST(lofar_top_srcdir)
  AC_SUBST(lofar_sharedir)
  AC_SUBST(LOFAR_DEPEND)
  AC_SUBST(CPPFLAGS)
  AC_SUBST(LDFLAGS)

])
