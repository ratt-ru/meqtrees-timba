#
# lofar_debugoptimise.m4
#
#
# lofar_DEBUG_OPTIMISE
#
# Set debugging or optmisation flags for CC and CXX
#
AC_DEFUN(lofar_DEBUG_OPTIMISE,dnl
[AC_PREREQ(2.13)dnl
AC_ARG_WITH(debug,
	[  --with-debug[=CFLAGS]   enable debugging CFLAGS [default="-g"]],
	[with_debug="$withval"],
	[with_debug=no])dnl
AC_ARG_WITH(optimise,
	[  --with-optimse[=CFLAGS] enable optimisation CFLAGS [default="-O3"]],
	[with_optimise="$withval"],
	[with_optimise=no])dnl
[
  if test "$with_debug" = "yes"; then
    if test "$GCC" = "yes"; then
	with_debug="-g -O2"
    else
	with_debug="-g"
    fi
  fi

  if test "$with_debug" != "no"; then
    CFLAGS="$with_debug";
    CXXFLAGS="$with_debug";
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
[ fi
  if test "$with_optimise" = "yes"; then
    with_optimise="-O3"
  fi

  if test "$with_optimise" != "no"; then
    CFLAGS="$with_optimise";
    CXXFLAGS="$with_optimise";
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
[ fi
  if test "$with_debug" != "no"; then
    if test "$with_optimise" != "no"; then]
AC_MSG_ERROR([Can not have both --with-debug and --with-optimise])
[
    fi
  fi
]])dnl