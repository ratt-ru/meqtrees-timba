#
# lofar_aips.m4
#
#
# lofar_AIPSPP
#
# Macro to check for AIPS++ installation
#
# lofar_AIPSPP
#
# e.g. lofar_AIPSPP
# -------------------------
#
AC_DEFUN(lofar_AIPSPP,dnl
[dnl
AC_PREREQ(2.13)dnl
AC_ARG_WITH(aipspp,
	[  --with-aipspp           enable use of AIPS++ (AIPSPATH environment variable needs to be set)],
	[with_aipspp=yes],
	[with_aipspp=no])
[
if test "$with_aipspp" = "yes"; then]
AC_MSG_CHECKING([whether AIPSPATH environment variable is set])
[	if test "${AIPSPATH+set}" != "set"; then]
AC_MSG_RESULT([no])
AC_MSG_ERROR([AIPSPATH not set!])
[ 	else]
AC_MSG_RESULT([yes])
[
		AIPSPP_PATH=`expr "$AIPSPATH" : "\(.*\) .* .* .*"`;
		AIPSPP_ARCH=`expr "$AIPSPATH" : ".* \(.*\) .* .*"`;

		case `uname -s` in
			SunOS)  arch=SOLARIS;;
			Linux)  arch=LINUX;;
			IRIX32) arch=IRIX;;
			IRIX64) arch=IRIX;;
			*)      arch=UNKNOWN;;
		esac

		AIPSPP_CFLAGS="-I$AIPSPP_PATH/code/include -DAIPS_$arch"
		AIPSPP_LDFLAGS="-L$AIPSPP_PATH/$AIPSPP_ARCH/lib"
		AIPSPP_LIBS="-laips"

		CFLAGS="$CFLAGS $AIPSPP_CFLAGS"
		CXXFLAGS="$CXXFLAGS $AIPSPP_CFLAGS -Wno-template-friend"
		LDFLAGS="$LDFLAGS $AIPSPP_LDFLAGS"
		LIBS="$LIBS $AIPSPP_LIBS"
]
dnl
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
dnl
AC_DEFINE(HAVE_AIPSPP, 1, [Define if AIPS++ is installed])dnl
[
	fi
fi
]
AM_CONDITIONAL(HAVE_AIPSPP, [test "$with_aipspp" = "yes"])
]
)
