#
# lofar_matlab.m4
#
#
# lofar_MATLAB
#
# Macro to check for MATLAB installation
#
# lofar_MATLAB([DEFAULT-PREFIX])
#
# e.g. lofar_MATLAB(["/usr/local/matlabr12"])
# -------------------------
#
AC_DEFUN(lofar_MATLAB,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_MATLAB_PREFIX,[/usr/local/matlabr12]), define(DEFAULT_MATLAB_PREFIX,$1))
AC_ARG_WITH(matlab,
	[  --with-matlab[=PFX]     prefix where Matlab is installed (default=]DEFAULT_MATLAB_PREFIX[)],
	[with_matlab=$withval],
	[with_matlab="no"])
[
if test "$with_matlab" = "no"; then
  enable_matlab=no
else
  if test "$with_matlab" = "yes"; then
    matlab_prefix=]DEFAULT_MATLAB_PREFIX
[
  else
    matlab_prefix=$withval
  fi
  enable_matlab=yes
]
##
## Check in normal location and suggested location
##
AC_CHECK_FILE([$matlab_prefix/extern/include/matlab.h],
			[lofar_cv_header_matlab=yes],
			[lofar_cv_header_matlab=no])dnl
[
  if test $lofar_cv_header_matlab = yes ; then

	MATLAB_PATH="$matlab_prefix"

	MATLAB_CPPFLAGS="-I$MATLAB_PATH/extern/include"
	MATLAB_LDFLAGS="-L$MATLAB_PATH/extern/lib/glnx86"
	MATLAB_LIBS="-lmx -leng"

	CPPFLAGS="$CPPFLAGS $MATLAB_CPPFLAGS"
	LDFLAGS="$LDFLAGS $MATLAB_LDFLAGS"
	LIBS="$LIBS $MATLAB_LIBS"
]
dnl
AC_SUBST(CPPFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
dnl
AC_DEFINE(HAVE_MATLAB, 1, [Define if Matlab is installed])dnl
[
  else]
AC_MSG_ERROR([Could not find Matlab in $matlab_prefix])
[
    enable_matlab=no
  fi
fi]
AM_CONDITIONAL(HAVE_MATLAB, [test "$enable_matlab" = "yes"])
])
