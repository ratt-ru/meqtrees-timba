#  lofar_aips.m4
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


# lofar_AIPSPP
#
# Macro to check for AIPS++ installation
# If AIPS++ functions are used that use LAPACK, lofar_LAPACK should
# also be made part of the configure.in (after lofar_AIPSPP).
#
# lofar_AIPSPP(option)
#     option 0 means that AIPS++ is optional, otherwise mandatory.
#
# e.g. lofar_AIPSPP
# -------------------------
#
AC_DEFUN([lofar_AIPSPP],dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], [lfr_option=0], [lfr_option=$1])
AC_ARG_WITH(aipspp,
	[  --with-aipspp[=PFX]         enable use of AIPS++ (via AIPSPATH or explicit path)],
	[with_aipspp="$withval"],
	[with_aipspp=""])
AC_ARG_WITH(pgplot,
	[  --with-pgplot[=PFX]         enable use of PGPLOT if needed by AIPS++],
	[with_pgplot="$withval"],
	[with_pgplot=""])
[
if test "$with_aipspp" = ""; then
  if test $lfr_option = "0"; then
    with_aipspp=no;
  else
    with_aipspp=yes;
  fi
fi
if test "$with_pgplot" = ""; then
    with_pgplot=no;
fi

if test "$with_aipspp" = "no"; then
  if test "$lfr_option" != "0"; then
    ]AC_MSG_ERROR([AIPS++ is needed, but --with-aipspp=no has been given])[
  fi
else
  if test "$with_aipspp" = "yes"; then
    ]AC_MSG_CHECKING([whether AIPSPATH environment variable is set])[
    if test "${AIPSPATH+set}" != "set"; then]
      AC_MSG_RESULT([no])
      AC_MSG_ERROR([AIPSPATH not set and no explicit path is given])
    [else]
      AC_MSG_RESULT([yes])
    [
      AIPSPP_PATH=`expr "$AIPSPATH" : "\(.*\) .* .* .*"`;
      AIPSPP_ARCH=`expr "$AIPSPATH" : ".* \(.*\) .* .*"`;
    fi
  else
    # A path like /aips++/daily/dop29_gnu has been given.
    # Last part is ARCH, rest is PATH.
    AIPSPP_PATH=`dirname $with_aipspp`;
    AIPSPP_ARCH=`basename $with_aipspp`;
  fi

  ]AC_CHECK_FILE([$AIPSPP_PATH/code/include],
	         [lfr_var1=yes], [lfr_var1=no])[
  ]AC_CHECK_FILE([$AIPSPP_PATH/$AIPSPP_ARCH/lib],
	         [lfr_var2=yes], [lfr_var2=no])[
  if test $lfr_var1 = yes  &&  test $lfr_var2 = yes; then
    case `uname -s` in
	SunOS)  arch=SOLARIS;;
	Linux)  arch=LINUX;;
	IRIX32) arch=IRIX;;
	IRIX64) arch=IRIX;;
	*)      arch=UNKNOWN;;
    esac

    AIPSPP_CPPFLAGS="-I$AIPSPP_PATH/code/include -DAIPS_$arch"
    if test "$lofar_compiler" = "kcc"; then
      AIPSPP_CPPFLAGS="$AIPSPP_CPPFLAGS -DAIPS_KAICC"
    fi
    AIPSPP_LDFLAGS="-L$AIPSPP_PATH/$AIPSPP_ARCH/lib -Wl,-rpath,$AIPSPP_PATH/$AIPSPP_ARCH/lib"
    # For one reason or another -ltrial -laips links in a lot of rubbish
    # (like MiriadImage). Therefore do -laips first.
    AIPSPP_LIBS="$AIPSPP_PATH/$AIPSPP_ARCH/lib/version.o -ltasking -lms -lfits -lmeasures -ltables -lscimath -lscimath_f -lcasa -lglish -lsos -lnpd"

    if test "$with_pgplot" != "no"; then
      ]AC_CHECK_FILE([$with_pgplot],
	             [lfr_pg=yes], [lfr_pg=no])[
      if test $lfr_pg = no; then
        ]AC_MSG_ERROR([given PGPLOT directory not found])[
      fi
      AIPSPP_LDFLAGS="$AIPSPP_LDFLAGS -L$with_pgplot"
      AIPSPP_LIBS="$AIPSPP_LIBS -lcpgplot -lpgplot"
    fi

    echo AIPSPP >> pkgext
    echo "$AIPSPP_CPPFLAGS" >> pkgextcppflags

    CPPFLAGS="$CPPFLAGS $AIPSPP_CPPFLAGS"
    if test "$lofar_compiler" = "gnu"; then
      CXXFLAGS="$CXXFLAGS -Wno-non-template-friend"
      echo "-Wno-non-template-friend" >> pkgextcxxflags
    fi
    LDFLAGS="$LDFLAGS $AIPSPP_LDFLAGS"
    LIBS="$LIBS $AIPSPP_LIBS"

  ]
dnl
    AC_SUBST(CPPFLAGS)dnl
    AC_SUBST(CXXFLAGS)dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
dnl
    AC_DEFINE(HAVE_AIPSPP, 1, [Define if AIPS++ is installed])dnl
[
  else
    ]AC_MSG_ERROR([AIPS++ installation not found])[
  fi
fi
]
AM_CONDITIONAL(HAVE_AIPSPP, [test "$with_aipspp" != "no"])
])
