#
# lofar_docxx.m4
#
#
# lofar_DOCXX
#
# Macro to check for DOCXX installation
#
# e.g. lofar_DOCXX
# -------------------------
#
AC_DEFUN(lofar_DOCXX,dnl
[dnl
AC_PREREQ(2.13)dnl
AC_ARG_WITH(docxx,
	[  --with-docxx[=PFX]  full path to a tool like DOC++ or DOXYGEN (default=doc++)],
	[force_docxx=yes; with_docxx="$withval"],
	[force_docxx=no; with_docxx="doc++"])dnl

AC_ARG_WITH(docxx-flags,
        [  --with-docxx-flags=FLAGS  specify DOCXX flags (default=--all --no-define --private --filenames --gifs --dir docxxhtml)],
        [with_docxx_flags="$withval"],
	[with_docxx_flags="yes"])dnl)

[
if test "$with_docxx" = "no"; then
  enable_docxx=no
else
  enable_docxx=yes
  docxx_path=$with_docxx
  if test "$with_docxx" = "yes"; then
    docxx_path=doc++
  fi]
  AC_CHECK_PROG(docxx_found,
		[$docxx_path],
		[$docxx_path],
		[""])
  [
  if test "$docxx_found" = ""; then
    enable_docxx=no
    if test "$force_docxx" = "yes"; then]
      AC_MSG_ERROR([Could not find documentation generator $docxx_path])
      [
    fi
  else
    DOCXX_PATH=$docxx_path

    DOCXX=$docxx_path
    DOCXXFLAGS="$with_docxx_flags"
    if test "$with_docxx_flags" = "no"; then
      DOCXXFLAGS=
    fi
    if test "$with_docxx_flags" = "yes"; then
      DOCXXFLAGS="--all --no-define --private --filenames --gifs --dir docxxhtml"
    fi
]
dnl
    AC_SUBST(DOCXX)dnl
    AC_SUBST(DOCXXFLAGS)dnl
dnl
[
    enable_docxx=no
  fi
fi
]
AM_CONDITIONAL(HAVE_DOCXX, [test "$enable_docxx" = "yes"])
])
