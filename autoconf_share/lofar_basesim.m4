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
AC_PREREQ(2.13)dnl
AC_ARG_WITH(basesim,
	[  --with-basesim[=PFX]    prefix where BaseSim is installed],
	[with_basesim=$withval],
	[with_basesim="no"])
[
if test "$with_basesim" = "no"; then
  enable_basesim=no
else
  if test "$with_basesim" = "yes"; then
    basesim_prefix=]DEFAULT_BASESIM_PREFIX
[
  else
    basesim_prefix=$withval
  fi
  enable_basesim=yes
]
##
## Check in normal location and suggested location
##
AC_CHECK_FILE([$basesim_prefix/libbasesim.la],
			[lofar_cv_lib_basesim=yes],
			[lofar_cv_lib_basesim=no])dnl
[
  if test $lofar_cv_lib_basesim = yes ; then

	BASESIM_PATH="$matlab_prefix"

	BASESIM_CFLAGS="-I$BASESIM_PATH/include"
	BASESIM_LDFLAGS="-L$BASESIM_PATH/extern/lib/glnx86"
	BASESIM_LIBS="-lmx -leng"

	CFLAGS="$CFLAGS $BASESIM_CFLAGS"
	CXXFLAGS="$CXXFLAGS $BASESIM_CFLAGS"
	LDFLAGS="$LDFLAGS $BASESIM_LDFLAGS"
	LIBS="$LIBS $BASESIM_LIBS"
]
dnl
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
dnl
dnl NOT NEEDED: AC_DEFINE(HAVE_BASESIM, 1, [Define if Matlab is installed])dnl
[
  else]
AC_MSG_ERROR([Could not find Matlab in $matlab_prefix])
[
    enable_matlab=no
  fi
fi]
dnl NOT NEEDED: AM_CONDITIONAL(HAVE_BASESIM, test "$enable_matlab" = "yes")
])
