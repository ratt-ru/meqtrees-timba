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
	[  --with-optimize[=CFLAGS]  enable optimization CFLAGS (default=-O3 or +K3)],
	[with_optimize="$withval"],
	[with_optimize=no])dnl
AC_ARG_ENABLE(tracer,
	[  --disable-tracer        disable TRACER macros],
	[enable_tracer="$enableval"],
	[enable_tracer=yes])dnl
AC_ARG_ENABLE(dbgassert,
	[  --enable-dbgassert      en/disable DBGASSERT macros (default is debug/opt)],
	[enable_dbgassert="$enableval"],
	[enable_dbgassert="default"])dnl
[
  if test "$with_debug" = "yes"; then
    with_debug="-g"
  fi

  if test "$lofar_compiler" = "gnu"; then
    lofar_warnflags="-W -Wall";
  fi
# Suppress KCC warnings about returning by const value and about double ;
  if test "$lofar_compiler" = "kcc"; then
    lofar_warnflags="--display_error_number --restrict --diag_suppress 815,381";
  fi

  enable_debug="no";
  if test "$with_debug" != "no"; then
    enable_debug="yes";
  else
    if test "$with_optimize" = "no"; then
      enable_debug="yes";
    fi
  fi
  if test "$enable_debug" != "no"; then
    CFLAGS="-g";
    CXXFLAGS="-g $lofar_warnflags";
    if test "$enable_dbgassert" = "default"; then
      enable_dbgassert="yes";
    fi
  fi

  if test "$with_optimize" = "yes"; then
    if test "$lofar_compiler" = "kcc"; then
      with_optimize="+K3"
    else
      with_optimize="-O3"
    fi
  fi

  if test "$with_optimize" != "no"; then
    CFLAGS="$with_optimize";
    CXXFLAGS="$with_optimize $lofar_warnflags";
    if test "$enable_dbgassert" = "default"; then
      enable_dbgassert="no";
    fi
  fi
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
[
  if test "$enable_tracer" != "no"; then]
    AC_DEFINE(ENABLE_TRACER,dnl
	1, [Define if TRACER is enabled])dnl
  [fi
  if test "$enable_dbgassert" != "no"; then]
    AC_DEFINE(ENABLE_DBGASSERT,dnl
	1, [Define if DbgAssert is enabled])dnl
  [fi

  if test "$with_debug" != "no"; then
    if test "$with_optimize" != "no"; then]
AC_MSG_ERROR([Can not have both --with-debug and --with-optimize])
[
    fi
  fi
]])dnl
