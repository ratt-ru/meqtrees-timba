#
# lofar_firewalls.m4
#
#
# lofar_FIREWALLS
#
# Enable or disable firewall code (asserts)
#
AC_DEFUN(lofar_FIREWALLS,dnl
[AC_PREREQ(2.13)dnl
AC_ARG_ENABLE(firewalls,
	[  --disable-firewalls     disable firewall code (do not check assertions)],
	[enable_firewalls=no], [enable_firewalls=yes])dnl
[if test "$enable_firewalls" = "yes"; then]
AC_DEFINE(HAVE_FIREWALLS, 1, [Define if firewall code should be used (assertions checked)])dnl
[fi]
])dnl
