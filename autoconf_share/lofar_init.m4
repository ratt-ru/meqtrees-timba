#
# lofar_init.m4
#
#
# lofar_INIT
#
# Macro to initialize common LOFAR make variables
#
AC_DEFUN(lofar_INIT,dnl
[dnl
AC_PREREQ(2.13)dnl
[
  lofar_top_srcdir=`(cd $srcdir && pwd) | sed -e "s%/LOFAR/.*%/LOFAR%"`
  lofar_sharedir=$lofar_top_srcdir/autoconf_share
]
  AC_SUBST(lofar_top_srcdir)
  AC_SUBST(lofar_sharedir)
])
