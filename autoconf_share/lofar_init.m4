#
# lofar_init.m4
#
#
# lofar_INIT
#
# Macro to initialize common LOFAR make variables and to
# define CXX if only CC is defined.
# It should be invoked before AC_PROG_CXX.
#
AC_DEFUN(lofar_INIT,dnl
[dnl
AC_PREREQ(2.13)dnl

[
  lofar_top_srcdir=`(cd $srcdir && pwd) | sed -e "s%/LOFAR/.*%/LOFAR%"`
  lofar_rem=`(cd $srcdir && pwd) | sed -e "s%$lofar_top_srcdir%%"`
  lofar_rest=`(echo $lofar_rem) | sed -e "s%/LOFAR/.*%/LOFAR%"`
  if test "$lofar_rem" != "$lofar_rest"; then
    ]AC_MSG_ERROR([Directory name LOFAR should be used only once in your path])[
  fi
  lofar_sharedir=$lofar_top_srcdir/autoconf_share
  if test "x$CC" != "x"; then
    if test "x$CXX" = "x"; then
      lofar_cxx=`basename $CC`;
      lofar_ccdir="";
      if test "x$lofar_cxx" != "x$CC"; then
        lofar_ccdir=`dirname $CC`/;
      fi
      if test "x$lofar_cxx" = "xgcc"; then
        lofar_cxx="g++";
      fi
      CXX="$lofar_ccdir$lofar_cxx";
      ]AC_SUBST(CXX)[
    fi
  fi
  if test "x$CXX" != "x"; then
    lofar_cxx=`basename $CXX`;
    if test "x$lofar_cxx" = "xKCC"; then
      AR="$CXX";
      AR_FLAGS="-o";
      ]AC_SUBST(AR)
       AC_SUBST(AR_FLAGS)[
    fi
  fi
]
  AC_SUBST(lofar_top_srcdir)
  AC_SUBST(lofar_sharedir)
])
