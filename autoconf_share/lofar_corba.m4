#
# lofar_corba.m4
#
#
# lofar_CORBA
#
# Macro to check for suitable Corba implmentation
#
AC_DEFUN(lofar_CORBA,dnl
lofar_HEADER_VISIBROKER([]))dnl
dnl
#
# lofar_HEADER_VISIBROKER([DEFAULT-PREFIX])
#
# e.g. lofar_HEADER_VISIBROKER("/var/local/inprise/vbroker")
# -------------------------
#
# Macro to check corba.h header file
#
AC_DEFUN(lofar_HEADER_VISIBROKER,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_VBROKER_PREFIX,[/opt/inprise/vbroker]), define(DEFAULT_VBROKER_PREFIX,$1))
AC_ARG_WITH(vbroker,
	[  --with-vbroker[=PFX]    prefix where Visibroker is installed (default=]DEFAULT_VBROKER_PREFIX[)],
	[with_vbroker=$withval],
	[with_vbroker="no"])
[
if test "$with_vbroker" = "no"; then
  enable_vbroker=no
else
  if test "$with_vbroker" = "yes"; then
    vbroker_prefix=]DEFAULT_VBROKER_PREFIX
[
  else
    vbroker_prefix=$withval
  fi
  enable_vbroker=yes
]
##
## Check in normal location and suggested location
##
AC_CHECK_FILE([$vbroker_prefix/include/corba.h],
			[lofar_cv_header_vbroker=yes],
			[lofar_cv_header_vbroker=no])
dnl
[
  if test $lofar_cv_header_vbroker = no; then
     vbroker_prefix="/usr/local/inprise/vbroker"]
##
## Check in alternative location
##
AC_CHECK_FILE([$vbroker_prefix/include/corba.h],
			[lofar_cv_header_vbroker=yes],
			[lofar_cv_header_vbroker=no])
[
  fi
  if test $lofar_cv_header_vbroker = yes ; then

	VBROKER_PATH="$vbroker_prefix"

	VBROKER_CFLAGS="-I$VBROKER_PATH/include"
	VBROKER_LDFLAGS="-L$VBROKER_PATH/lib"
	VBROKER_LIBS="-lcosev_r -lcosnm_r -lvport_r -lorb_r -lpthread"

	CFLAGS="$CFLAGS $VBROKER_CFLAGS"
	CXXFLAGS="$CXXFLAGS $VBROKER_CFLAGS"
	LDFLAGS="$LDFLAGS $VBROKER_LDFLAGS"
	LIBS="$LIBS $VBROKER_LIBS"
	IDLCXX="$vbroker_prefix/bin/idl2cpp"
	IDLFLAGS=""
]
dnl
AC_SUBST(CFLAGS)dnl
AC_SUBST(CXXFLAGS)dnl
AC_SUBST(LDFLAGS)dnl
AC_SUBST(LIBS)dnl
AC_SUBST(IDLCXX)dnl
AC_SUBST(IDLFLAGS)dnl
dnl
AM_CONDITIONAL(HAVE_CORBA, true)
AC_DEFINE(HAVE_CORBA, 1, [Define if Inprise Visibroker Corba installed])dnl
[
  else]
AC_MSG_ERROR([Could not find Inprise Visibroker in $vbroker_prefix])
[
    enable_vbroker=no
  fi
fi]
])
