#
# lofar_basesim.m4
#
#
# lofar_BASESIM
#
# Macro to check for BASESIM installation
#
#  It adds the BaseSim include directory to CPPFLAGS
#  and the BaseSim library directory to LIBS.
#
#  --with-basesim  tries to find the paths automatically.
#                  include path is derived from $srcdir
#                  library path is derived from `pwd`
#  --with-basesim=PFX  specifies basic BaseSim path explicitly.
#                      derived include path gets PFX/src
#                      derived library path gets PFX/build
#  --with-basesim-include=PFX  overrides BaseSim derived include path.
#  --with-basesim-libdir=PFX   overrides BaseSim derived library path.
#
# lofar_BASESIM
#
# e.g. lofar_BASESIM
# -------------------------
#
AC_DEFUN(lofar_BASESIM,dnl
[dnl
AC_PREREQ(2.13)dnl
AC_ARG_WITH(basesim,
	[  --with-basesim[=PFX]    path to BaseSim directory],
	[with_basesim=$withval
         if test "${with_basesim}" != yes; then
            lofar_basesim_include="$withval/src"
            lofar_basesim_libdir="$withval/build"
         fi])

AC_ARG_WITH(basesim-include,
[  --with-basesim-include=PFX  specify include dir for BaseSim headers],
[lofar_basesim_include="$withval"])

AC_ARG_WITH(basesim-libdir,
[  --with-basesim-libdir=PFX   specify library dir for BaseSim library],
[lofar_basesim_libdir="$withval"])


[
enable_basesim=yes
if test "$with_basesim" = "no"; then]
AC_MSG_ERROR([Cannot configure without BaseSim])
[fi

# Try to guess where the BaseSim include directory is located.
# srcdir gives the current source directory; BaseSim is assumed to
# be in something/LOFAR/BaseSim/src.
#
lofar_curwd=`pwd`
lofar_srcdir=`cd $srcdir && pwd`
if test "$lofar_basesim_include" = ""; then
  lofar_base=`echo $lofar_srcdir | sed -e "s%/LOFAR/.*%/LOFAR%"`
  lofar_basesim_include=$lofar_base/BaseSim/src
fi

# Try to guess where the BaseSim library directory is located.
# pwd gives the current build directory, which can be something
# like   something/package/something
# It simply replaces package by BaseSim.
# Note that package is the last part of the source directory.
#
if test "$lofar_basesim_libdir" = ""; then
  lofar_pkg=`echo $lofar_srcdir | sed -e "s%.*/LOFAR/%%"`
  lofar_basesim_libdir=`echo $lofar_curwd | sed -e "s%/$lofar_pkg%/BaseSim%"`
fi

## Check if the build directory is valid.
## The library might not be there yet, but it must have been configured,
## so a libtool should be there.
##
## Check for BaseSim.h header file in src dir.
##
]
AC_CHECK_FILE([$lofar_basesim_libdir/libtool],
			[lofar_cv_lib_basesim=yes],
			[lofar_cv_lib_basesim=no])
AC_CHECK_FILE([$lofar_basesim_include/BaseSim.h],
			[lofar_cv_hdr_basesim=yes],
			[lofar_cv_hdr_basesim=no])dnl
[
if test $lofar_cv_hdr_basesim = yes  &&  test $lofar_cv_lib_basesim = yes; then
  # Turn possible relative paths into absolute paths, because
  # relative paths can miss some .. parts.
  lofar_basesim_include=`cd $lofar_basesim_include && pwd`
  lofar_basesim_libdir=`cd $lofar_basesim_libdir && pwd`
  CPPFLAGS="$CPPFLAGS -I$lofar_basesim_include"
  LIBS="$LIBS $lofar_basesim_libdir/src/libbasesim.la"

  # Two new variables for use in Makefile.am's
  basesim_top_srcdir="$lofar_basesim_include"
  basesim_top_builddir="$lofar_basesim_libdir"
]
dnl
AC_SUBST(CPPFLAGS)dnl
AC_SUBST(LIBS)dnl
AC_SUBST(basesim_top_srcdir)dnl
AC_SUBST(basesim_top_builddir)dnl
dnl
dnl NOT NEEDED: AC_DEFINE(HAVE_BASESIM, 1, [Define if BaseSim is installed])dnl
[
else
  if test $lofar_cv_hdr_basesim = no; then]
AC_MSG_ERROR([Could not find BaseSim.h in $lofar_basesim_include])
[
    enable_basesim=no
  else]
AC_MSG_ERROR([Could not find libtool in $lofar_basesim_libdir])
[
  fi
fi
]
dnl NOT NEEDED: AM_CONDITIONAL(HAVE_BASESIM, test "$enable_basesim" = "yes")
])
