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
AC_ARG_WITH(cppflags,
	[  --with-cppflags=CPPFLAGS  enable extra CPPFLAGS],
	[with_cppflags="$withval"])dnl
AC_ARG_WITH(cflags,
	[  --with-cflags=CFLAGS      enable extra CFLAGS],
	[with_cflags="$withval"])dnl
AC_ARG_WITH(cxxflags,
	[  --with-cxxflags=CXXFLAGS  enable extra CXXFLAGS],
	[with_cxxflags="$withval"])dnl
AC_ARG_WITH(ldflags,
	[  --with-ldflags=LDFLAGS    enable extra LDFLAGS],
	[with_ldflags="$withval"])dnl
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
    lofar_warnflags="-W -Wall -Wno-unknown-pragmas";
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
  if test "$enable_debug" = "yes"; then]
AC_DEFINE(LOFAR_DEBUG,dnl
	1, [Define if we are compiling with debugging information])dnl
[ fi
  if test "$enable_debug" != "no"; then
    lfr_cflags="-g";
    lfr_cxxflags="-g $lofar_warnflags";
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
    lfr_cflags="$with_optimize";
    lfr_cxxflags="$with_optimize $lofar_warnflags";
    if test "$enable_dbgassert" = "default"; then
      enable_dbgassert="no";
    fi
  fi

  CPPFLAGS="$CPPFLAGS $with_cppflags"
  CFLAGS="$lfr_cflags $with_cflags"
  CXXFLAGS="$lfr_cxxflags $with_cxxflags"
  LDFLAGS="$LDFLAGS $with_ldflags"
]
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(CPPFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
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
