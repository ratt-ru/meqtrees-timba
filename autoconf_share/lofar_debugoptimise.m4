#
# lofar_debugoptimise.m4
#
#
# lofar_DEBUG_OPTIMIZE
#
# Set debugging or optmisation flags for CC and CXX
#
AC_DEFUN(lofar_DEBUG_OPTIMIZE,dnl
[AC_PREREQ(2.13)dnl
AC_ARG_WITH(debug,
	[  --with-debug[=CFLAGS]   enable debugging CFLAGS [default="-g"]],
	[with_debug="$withval"],
	[with_debug=no])dnl
AC_ARG_WITH(optimize,
	[  --with-optimize[=CFLAGS] enable optimization CFLAGS [default="-O3"]],
	[with_optimize="$withval"],
	[with_optimize=no])dnl
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
  if test "$with_optimize" = "yes"; then
    with_optimize="-O3"
  fi

  if test "$with_optimize" != "no"; then
    CFLAGS="$with_optimize";
    CXXFLAGS="$with_optimize";
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
[ fi
  if test "$with_debug" != "no"; then
    if test "$with_optimize" != "no"; then]
AC_MSG_ERROR([Can not have both --with-debug and --with-optimize])
[
    fi
  fi
]])dnl
