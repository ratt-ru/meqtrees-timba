#
# lofar_basesim.m4
#
#
# lofar_BASESIM
#
# Macro to check for BASESIM installation
#
# lofar_BASESIM
#
# e.g. lofar_BASESIM
# -------------------------
#
AC_DEFUN(lofar_BASESIM,dnl
[dnl
[MODULEBASE=]$1
AC_PREREQ(2.13)dnl
AC_ARG_WITH(basesim,
	[  --with-basesim[=PFX]    path to BaseSim build directory],
	[with_basesim=$withval],
	[with_basesim="yes"])
[
enable_basesim=yes
if test "$with_basesim" = "no"; then]
AC_MSG_ERROR([Cannot configure without BaseSim])
[fi
if test "$with_basesim" = "yes"; then

  #
  # Try to guess where the BaseSim directory is located
  # Construct lofar_basesim_top_builddir
  #
  rel_top_builddir=`echo $PWD | sed -e "s%.*/$MODULEBASE/%%"`
  lofar_base=`echo $PWD | sed -e "s%/LOFAR/.*%/LOFAR%"`
  lofar_basesim_top_builddir=$lofar_base/BaseSim/$rel_top_builddir
  lofar_basesim_top_srcdir=$lofar_base/BaseSim/src

  # debugging echo statements
  # echo rel_top_builddir = $rel_top_builddir
  # echo lofar_base       = $lofar_base
  # echo lofar_basesim_top_builddir = $lofar_basesim_top_builddir
  # echo lofar_basesim_top_srcdir   = $lofar_basesim_top_srcdir

  # Strip everything upto LOFAR component from start of pwd
  # set BaseSim path to 

else

  lofar_basesim_top_builddir=$withval

  lofar_basesim_top_srcdir=`echo $withval | sed -e "s%/BaseSim/.*%/BaseSim%"`
  lofar_basesim_top_srcdir=$lofar_basesim_top_srcdir/src

  # debugging echo statements
  # echo lofar_basesim_top_builddir = $lofar_basesim_top_builddir
  # echo lofar_basesim_top_srcdir   = $lofar_basesim_top_srcdir
  
fi
]
##
## Check for BaseSim.h header file in src dir
##
AC_CHECK_FILE([$lofar_basesim_top_srcdir/BaseSim.h],
			[lofar_cv_header_basesim=yes],
			[lofar_cv_header_basesim=no])dnl
[
  if test $lofar_cv_header_basesim = yes ; then

	CFLAGS="$CFLAGS -I$lofar_basesim_top_srcdir"
	CXXFLAGS="$CXXFLAGS -I$lofar_basesim_top_srcdir"
	LIBS="$LIBS $lofar_basesim_top_builddir/src/libbasesim.la"

	# Two new variable for use in Makefile.am's
	basesim_top_srcdir="$lofar_basesim_top_srcdir"
	basesim_top_builddir="$lofar_basesim_top_builddir"
]
dnl
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(LIBS)dnl
AC_SUBST(basesim_top_srcdir)dnl
AC_SUBST(basesim_top_builddir)dnl
dnl
dnl NOT NEEDED: AC_DEFINE(HAVE_BASESIM, 1, [Define if Matlab is installed])dnl
[
  else]
AC_MSG_ERROR([Could not find BaseSim installation in $lofar_basesim_top_srcdir])
[
    enable_basesim=no
  fi
]
dnl NOT NEEDED: AM_CONDITIONAL(HAVE_BASESIM, test "$enable_matlab" = "yes")
])
