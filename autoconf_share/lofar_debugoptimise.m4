#
# lofar_debugoptimise.m4
#
#
# lofar_DEBUG_OPTIMIZE
#
# Set debugging or optmisation flags for CC and CXX
#
AC_DEFUN(lofar_DEBUG_OPTIMIZE,dnl
[dnl
AC_PREREQ(2.13)dnl
AC_ARG_WITH(debug,
	[  --with-debug[=CFLAGS]     enable debugging CFLAGS (default=-g)],
	[with_debug="$withval"],
	[with_debug=no])dnl
AC_ARG_WITH(optimize,
	[  --with-optimize[=CFLAGS]  enable optimization CFLAGS (default=-O3)],
	[with_optimize="$withval"],
	[with_optimize=no])dnl
[
  if test "$with_debug" = "yes"; then
    with_debug="-g"
  fi

  if test "$with_debug" != "no"; then
    CFLAGS="$with_debug";
    CXXFLAGS="$with_debug -W -Wall";
  else
    if test "$with_optimize" = "no"; then
      CFLAGS="-g";
      CXXFLAGS="-g -W -Wall";
    fi
  fi

  if test "$with_optimize" = "yes"; then
    with_optimize="-O3"
  fi

  if test "$with_optimize" != "no"; then
    CFLAGS="$with_optimize";
    CXXFLAGS="$with_optimize -W -Wall";
  fi
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
[
  if test "$with_debug" != "no"; then
    if test "$with_optimize" != "no"; then]
AC_MSG_ERROR([Can not have both --with-debug and --with-optimize])
[
    fi
  fi
]])dnl
