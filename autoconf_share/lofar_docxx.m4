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
lofar_DOXYGEN([])dnl
lofar_DOCPP([])dnl
[
if test "$enable_doxygen" = "yes"; then
  if test "$enable_docpp" = "yes"; then
]
    AC_MSG_ERROR([Cannot use both doxygen and doc++ tools. Reconfigure with --without-doxygen or --without-docpp])
[ fi
fi]
)dnl
#
#
#
# lofar_DOXYGEN
#
# Macro to check for and enable documentation generation with doxygen
#
# e.g. lofar_DOXYGEN(["/local/bin"])
# -------------------------
#
AC_DEFUN(lofar_DOXYGEN,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_DOXYGEN_PREFIX,[/local/bin]), define(DEFAULT_DOXYGEN_PREFIX,$1))
AC_ARG_WITH(doxygen,
	[  --with-doxygen[=PFX]      directory of DOXYGEN tool (default=/local/bin)],
	[force_doxygen=yes; with_doxygen="$withval"],
	[force_doxygen=no; with_doxygen="/local/bin"])dnl

AC_ARG_WITH(doxygen-dot,
        [  --with-doxygen-dot[=PFX]  directory of GraphViz dot tool (default=/local/bin)],
        [with_doxygen_dot="$withval"],
	[with_doxygen_dot="no"])dnl

[
if test "$with_doxygen" = "no"; then
  enable_doxygen=no
else
  enable_doxygen=yes
  doxygen_path=$with_doxygen
  if test "$with_doxygen" = "yes"; then
    doxygen_path=]DEFAULT_DOXYGEN_PREFIX
  [
  fi]
  AC_CHECK_PROG(doxygen_found, doxygen,
		[$doxygen_path],
		[""],
		[$doxygen_path])
  [
  if test "$doxygen_found" = ""; then
    enable_doxygen=no
    if test "$force_doxygen" = "yes"; then]
      AC_MSG_ERROR([Could not find documentation tool $doxygen_path/doxygen])
      [
    fi
  else
    DOXYGEN=$doxygen_path/doxygen

    \rm -f .doxygenrc
    touch .doxygenrc
    echo 'OUTPUT_DIRECTORY	= .' >> .doxygenrc
    echo 'EXTRACT_ALL		= YES' >> .doxygenrc
    echo 'EXTRACT_PRIVATE	= YES' >> .doxygenrc
    echo 'EXTRACT_STATIC	= YES' >> .doxygenrc
    echo 'ALWAYS_DETAILED_SEC	= YES' >> .doxygenrc
    echo 'CASE_SENSE_NAMES	= YES' >> .doxygenrc
    echo 'DISTRIBUTE_GROUP_DOC	= YES' >> .doxygenrc
    echo 'ALIASES		= "template=\par Template requirements:\n"' >> .doxygenrc
    echo 'MAX_INITIALIZER_LINES	= 0' >> .doxygenrc
    echo 'WARNINGS		= YES' >> .doxygenrc
    echo 'WARN_IF_UNDOCUMENTED	= NO' >> .doxygenrc
    echo 'FILE_PATTERNS		= "*.h" "*.idl"' >> .doxygenrc
    echo 'SOURCE_BROWSER	= YES' >> .doxygenrc
    echo 'REFERENCED_BY_RELATION= YES' >> .doxygenrc
    echo 'REFERENCES_RELATION	= YES' >> .doxygenrc
    echo 'ALPHABETICAL_INDEX	= YES' >> .doxygenrc
    echo 'HTML_OUTPUT		= "docxxhtml"' >> .doxygenrc
    echo 'ENUM_VALUES_PER_LINE	= 1' >> .doxygenrc
    echo 'GENERATE_TREEVIEW	= YES' >> .doxygenrc
    echo 'GENERATE_LATEX	= NO' >> .doxygenrc
    echo 'GENERATE_TAGFILE	= base.tag' >> .doxygenrc
    echo 'ALLEXTERNALS		= YES' >> .doxygenrc
    echo '' >> .doxygenrc
    echo 'SEARCHENGINE		= NO' >> .doxygenrc
    
    if test "$with_doxygen_dot" != "no"; then
      doxygen_dot=$with_doxygen_dot
      if test "$with_doxygen_dot" = "yes"; then
        doxygen_dot=]DEFAULT_DOXYGEN_PREFIX
      [
      fi]
      AC_CHECK_PROG(doxygen_dot_found, dot,
		    [$doxygen_dot],
		    [""],
		    [$doxygen_dot])
      [
      if test "$doxygen_dot_found" = ""; then
        if test "$force_doxygen" = "yes"; then]
          AC_MSG_ERROR([Could not find GraphViz tool $doxygen_dot/dot])
          [
        fi
      else
        DOXYGENDOT="$doxygen_dot/dot"
	echo 'HAVE_DOT = YES' >> .doxygenrc
	echo 'CLASS_GRAPH = YES' >> .doxygenrc
	echo 'COLLABORATION_GRAPH = YES' >> .doxygenrc
	echo "DOT_PATH = $doxygen_dot" >> .doxygenrc
	echo 'DOT_CLEANUP = YES' >> .doxygenrc
	echo '' >> .doxygenrc
      fi
    fi
]
dnl
    AC_SUBST(DOXYGEN)dnl
dnl
[
  fi
fi
]
AM_CONDITIONAL(HAVE_DOXYGEN, [test "$enable_doxygen" = "yes"])
])
#
#
#
# lofar_DOCPP
#
# Macro to check for and enable documentation generation with doc++
#
# e.g. lofar_DOC++(["/local/bin"])
# -------------------------
#
AC_DEFUN(lofar_DOCPP,dnl
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(DEFAULT_DOCPP_PREFIX,[/local/bin]), define(DEFAULT_DOCPP_PREFIX,$1))
AC_PREREQ(2.13)dnl
AC_ARG_WITH(docpp,
	[  --with-docpp[=PFX]        directory of DOCPP tool (default=/local/bin)],
	[force_docpp=yes; with_docpp="$withval"],
	[force_docpp=no; with_docpp="/local/bin"])dnl

AC_ARG_WITH(docpp-flags,
        [  --with-docpp-flags=FLAGS  specify DOCPP flags (default=--all --no-define --private --filenames --gifs --dir docxxhtml)],
        [with_docpp_flags="$withval"],
	[with_docpp_flags="yes"])dnl

[
if test "$with_docpp" = "no"; then
  enable_docpp=no
else
  enable_docpp=yes
  docpp_path=$with_docpp
  if test "$with_docpp" = "yes"; then
    docpp_path=]DEFAULT_DOCPP_PREFIX
  [
  fi]
  AC_CHECK_PROG(docpp_found, doc++,
		[$docpp_path],
		[""],
		[$docpp_path])
  [
  if test "$docpp_found" = ""; then
    enable_docpp=no
    if test "$force_docpp" = "yes"; then]
      AC_MSG_ERROR([Could not find documentation tool $docpp_path/doc++])
      [
    fi
  else
    DOCPP=$docpp_path/doc++
    DOCPPFLAGS="$with_docpp_flags"
    if test "$with_docpp_flags" = "no"; then
      DOCPPFLAGS=
    fi
    if test "$with_docpp_flags" = "yes"; then
      DOCPPFLAGS="--all --no-define --private --filenames --gifs --dir docxxhtml"
    fi
]
dnl
    AC_SUBST(DOCPP)dnl
    AC_SUBST(DOCPPFLAGS)dnl
dnl
[
  fi
fi
]
AM_CONDITIONAL(HAVE_DOCPP, [test "$enable_docpp" = "yes"])
])
