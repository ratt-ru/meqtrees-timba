#
# lofar_aips.m4
#
#
# lofar_AIPSPP
#
# Macro to check for AIPS++ installation
#
# lofar_AIPSPP(option)
#     option 0 means that AIPS++ is optional, otherwise mandatory.
#
# e.g. lofar_AIPSPP
# -------------------------
#
AC_DEFUN(lofar_AIPSPP,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], [lfr_option=0], [lfr_option=$1])
AC_ARG_WITH(aipspp,
	[  --with-aipspp[=PFX]         enable use of AIPS++ (via AIPSPATH or explicit path)],
	[with_aipspp="$withval"],
	[with_aipspp=""])
[
if test "$with_aipspp" = ""; then
  if test $lfr_option = "0"; then
    with_aipspp=no;
  else
    with_aipspp=yes;
  fi
fi

if test "$with_aipspp" = "no"; then
  if test "$lfr_option" != "0"; then
    ]AC_MSG_ERROR([AIPS++ is needed, but --with-aipspp=no has been given])[
  fi
else
  if test "$with_aipspp" = "yes"; then
    ]AC_MSG_CHECKING([whether AIPSPATH environment variable is set])[
    if test "${AIPSPATH+set}" != "set"; then]
      AC_MSG_RESULT([no])
      AC_MSG_ERROR([AIPSPATH not set and no explicit path is given])
    [else]
      AC_MSG_RESULT([yes])
    [
      AIPSPP_PATH=`expr "$AIPSPATH" : "\(.*\) .* .* .*"`;
      AIPSPP_ARCH=`expr "$AIPSPATH" : ".* \(.*\) .* .*"`;
    fi
  else
    # A path like /aips++/daily/dop29_gnu has been given.
    # Last part is ARCH, rest is PATH.
    AIPSPP_PATH=`dirname $with_aipspp`;
    AIPSPP_ARCH=`basename $with_aipspp`;
  fi

  ]AC_CHECK_FILE([$AIPSPP_PATH/code/include],
	         [lfr_var1=yes], [lfr_var1=no])[
  ]AC_CHECK_FILE([$AIPSPP_PATH/$AIPSPP_ARCH/lib],
	         [lfr_var2=yes], [lfr_var2=no])[
  if test $lfr_var1 = yes  &&  test $lfr_var2 = yes; then
    case `uname -s` in
	SunOS)  arch=SOLARIS;;
	Linux)  arch=LINUX;;
	IRIX32) arch=IRIX;;
	IRIX64) arch=IRIX;;
	*)      arch=UNKNOWN;;
    esac

    AIPSPP_CPPFLAGS="-I$AIPSPP_PATH/code/include -DAIPS_$arch"
    AIPSPP_LDFLAGS="-L$AIPSPP_PATH/$AIPSPP_ARCH/lib"
    AIPSPP_LIBS="-ltrial -laips -ltrial_f -laips_f"

    CPPFLAGS="$CPPFLAGS $AIPSPP_CPPFLAGS"
    if test "$lofar_compiler" = "gnu"; then
      CXXFLAGS="$CXXFLAGS -Wno-non-template-friend"
    fi
    LDFLAGS="$LDFLAGS $AIPSPP_LDFLAGS"
    LIBS="$LIBS $AIPSPP_LIBS"
  ]
dnl
    AC_SUBST(CPPFLAGS)dnl
    AC_SUBST(CXXFLAGS)dnl
    AC_SUBST(LDFLAGS)dnl
    AC_SUBST(LIBS)dnl
dnl
    AC_DEFINE(HAVE_AIPSPP, 1, [Define if AIPS++ is installed])dnl
[
  else
    ]AC_MSG_ERROR([AIPS++ installation not found])[
  fi
fi
]
AM_CONDITIONAL(HAVE_AIPSPP, [test "$with_aipspp" != "no"])
])
