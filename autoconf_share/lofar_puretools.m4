#
# lofar_puretools.m4
#
#
# lofar_PURETOOLS
#
# Macro to check for and enable compilation/link with
# purify, quantify and purecov
#
# e.g. lofar_PURETOOLS(["/opt/pure/purify"])
# -------------------------
#
AC_DEFUN(lofar_PURETOOLS,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_PURETOOLS_PREFIX,[/opt/pure]), define(DEFAULT_PURETOOLS_PREFIX,$1))
AC_ARG_WITH(puretools,
	[  --with-puretools[=PFX]  prefix where Rational Purify, Quantify or Pure Coverage is installed (default=]DEFAULT_PURETOOLS_PREFIX[)],
	[force_puretools=yes; with_puretools="$withval"],
	[force_puretools=no;  with_puretools="yes"])dnl
[
if test "$with_puretools" = "no"; then
  enable_puretools=no
else
  if test "$with_puretools" = "yes"; then
    puretools_prefix=]DEFAULT_PURETOOLS_PREFIX
[
  else
    puretools_prefix=$withval
  fi
]
#
# Check for purify, quantify and purecov
#
AC_MSG_CHECKING([for purify, quantify and purecov in $puretools_prefix])
AC_MSG_RESULT([])
AC_CHECK_FILE([$puretools_prefix/purify/purify.h],
		[lofar_cv_purify_lib=yes],
		[lofar_cv_purify_lib=no])
AC_CHECK_FILE([$puretools_prefix/purify/libpurify_stubs.a],
		[lofar_cv_purify_lib="$lofar_cv_purify_lib yes"],
		[lofar_cv_purify_lib="$lofar_cv_purify_lib no"])
AC_CHECK_FILE([$puretools_prefix/purify/purify],
		[lofar_cv_purify=yes],
		[lofar_cv_purify=no])
AC_CHECK_FILE([$puretools_prefix/quantify/quantify],
		[lofar_cv_quantify=yes],
		[lofar_cv_quantify=no])
AC_CHECK_FILE([$puretools_prefix/purecov/purecov],
		[lofar_cv_purecov=yes],
		[lofar_cv_purecov=no])
dnl
[
  have_puretools=no;
  have_purify=0;
  have_quantify=0;
  have_purecov=0;
  if test $lofar_cv_purify = yes ; then
    have_purify=1;
    have_puretools=yes;
    if test "$lofar_cv_purify_lib" = "yes yes"; then ]
AC_DEFINE(HAVE_PURIFY, 1, [Define if using Rational Purify])dnl
[	CFLAGS="$CFLAGS -I$puretools_prefix/purify"
	CXXFLAGS="$CXXFLAGS -I$puretools_prefix/purify"
	LDFLAGS="$LDFLAGS -L$puretools_prefix/purify"
	LIBS="$LIBS -lpurify_stubs"
    fi
  fi
  if test $lofar_cv_quantify = yes ; then
    have_quantify=1;
    have_puretools=yes;
  fi
  if test $lofar_cv_purecov = yes ; then
    have_purecov=1;
    have_puretools=yes;
  fi

  if test $have_puretools = yes ; then

	PURETOOLS_PATH="$puretools_prefix"

	CC='$(top_srcdir)'"/puretool $have_purify $have_quantify $have_purecov "'$(top_builddir)'" $puretools_prefix $CC"
	CXX='$(top_srcdir)'"/puretool $have_purify $have_quantify $have_purecov "'$(top_builddir)'" $puretools_prefix $CXX"
]
dnl
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
AC_SUBST(CC)dnl
AC_SUBST(CXX)dnl
dnl
[
  else
    if test "$force_puretools" = "yes"; then]
AC_MSG_ERROR([Could not find Rational Purify, Quantify or Pure Coverage in $puretools_prefix])
[
    fi
    enable_puretools=no
  fi
fi]
])
