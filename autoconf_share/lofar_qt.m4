#
# lofar_qt.m4
#
#
# lofar_QT
#
# Macro to check for QT installation
#
# lofar_QT([DEFAULT-PREFIX])
#
# e.g. lofar_QT(["/usr/local/qtr12"])
# -------------------------
#
AC_DEFUN(lofar_QT,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_QT_PREFIX,[/usr/lib/qt-2.3.1]), define(DEFAULT_QT_PREFIX,$1))
AC_ARG_WITH(qt,
	[  --with-qt[=PFX]     prefix where Qt is installed (default=]DEFAULT_QT_PREFIX[)],
	[with_qt=$withval],
	[with_qt="no"])
[
if test "$with_qt" = "no"; then
  enable_qt=no
else
  if test "$with_qt" = "yes"; then
    qt_prefix=]DEFAULT_QT_PREFIX[
  else
    qt_prefix=$withval
  fi
  enable_qt=yes
]
##
## Check in normal location and suggested location
##
AC_CHECK_FILE([$qt_prefix/include/qt.h],
			[lofar_cv_header_qt=yes],
			[lofar_cv_header_qt=no])dnl
[
  if test $lofar_cv_header_qt = yes ; then

	QT_PATH="$qt_prefix"

	QT_CPPFLAGS="-I$QT_PATH/include"
	QT_LDFLAGS="-L$QT_PATH/lib"
	QT_LIBS="-lqt"

	CPPFLAGS="$CPPFLAGS $QT_CPPFLAGS"
	LDFLAGS="$LDFLAGS $QT_LDFLAGS"
	LIBS="$LIBS $QT_LIBS"
	QT_DIR="$QT_PATH"
]
dnl
AC_SUBST(CPPFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
AC_SUBST(QT_DIR)dnl
dnl
AC_DEFINE(HAVE_QT, 1, [Define if Qt is installed])dnl
[
  else]
AC_MSG_ERROR([Could not find Qt in $qt_prefix])
[
    enable_qt=no
  fi
fi]
AM_CONDITIONAL(HAVE_QT, [test "$enable_qt" = "yes"])
])
