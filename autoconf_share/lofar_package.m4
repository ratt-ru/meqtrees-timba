#
# lofar_package.m4
#
#
# lofar_PACKAGE
#
# Macro to check for the installation of a package
#
#  It creates a symlink to the package include directory and
#  symlinks to the package library.
#  The library name is added to the LIBS list.
#  
#  Note that a package is a directory with its own src subdirectory.
#  E.g. BaseSim or CEP/CPA/PSCF.
#  E.g. BaseSim/src/Corba is not a package and its object files
#  must be part of the main BaseSim library.
#
#  The package source files are part of the LOFAR tree.
#  The package library resides in a build area which can be anywhere.
#  The build area has subdirectories containing the build variant
#  like gnu_debug. This subdirectory is used for the build.
#  It can be found automatically if it resides in a standard build area
#  which can be:
#  1. A subdirectory build of the source tree (possibly using a symlink).
#  2. In a directory structure similar to the currently used build area.
#     E.g. if building in somewhere/MyPackage/build/x, a package BaseSim
#     is automatically found if it resides in somewhere/BaseSim/build/x.
#     Similarly, if building in somewhere/build/x/MyPackage, BaseSim
#     is automatically found if residing in somewhere/build/x/BaseSim.
#
#  The lofar root (see lofar_init.m4) sets the root of the system LOFAR
#  directory to use (e.g. lofar/daily).
#  
#  It is possible that the build area is elsewhere, but in that case
#  it need to be given explicitly using --with-package-libdir.
#
#  --with-package  tries to find the paths automatically.
#                  include path is derived from $srcdir
#                  library path is derived from `pwd`
#  --with-package=PFX  specifies basic package path explicitly.
#                      derived include path gets PFX/src
#                      derived library path gets PFX/build
#  --with-package-libdir=PFX   overrides package derived library path.
#
# lofar_PACKAGE(package_path, option)
#     where option=0 means that makepkglinks descends recursively into
#                    all packages used by this package.
#           option=1 means not recursively
#           option=2 means not recursively and no library in LIBS
#
# e.g. lofar_PACKAGE(CEP/CPA/PSCF)
# -------------------------
#
AC_DEFUN(lofar_PACKAGE,dnl
[dnl
AC_PREREQ(2.13)dnl
define(LOFAR_PKG_SYM,m4_patsubst([$1], [.*/]))
define(LOFAR_PKG_LIB,m4_tolower(m4_patsubst([$1], [.*/])))
ifelse($2, [], [lfr_option=0], [lfr_option=$2])
AC_ARG_WITH([LOFAR_PKG_LIB],
	[  --with-LOFAR_PKG_LIB[[=PFX]]        path to $1 directory],
	[with_package=$withval
         if test "${with_package}" = yes; then
            with_package=
         fi],
	[with_package=])

AC_ARG_WITH([LOFAR_PKG_LIB][[-libdir]],
  [  --with-LOFAR_PKG_LIB[-libdir]=PFX   specific library dir for $1 library],
  [lfr_package_libdir="$withval"],
  [lfr_package_libdir=])


[
enable_package=yes
if test "$with_package" = "no"; then]
AC_MSG_ERROR([Cannot configure without package $1])
[fi

# Try to guess where the package include directory is located.
# srcdir gives the current source directory; package is assumed to
# be in $lofar_top_srcdir/package/src.
#
lfr_curwd=`pwd`;
lfr_curdir=`basename $lfr_curwd`;
lfr_srcdir=`cd $srcdir && pwd`;
lfr_variant=;
lfr_root=;

# Handle a version and/or variant in a similar way as done in lofar_init.m4.
lfr_root="$with_package"
case "$with_package" in
*:*)
  lfr_root=`echo ${with_package} | sed -e "s/:.*//"`
  lfr_variant=`echo ${with_package} | sed -e "s/.*://"`
  ;;
esac

# If no version is given, use local one if available. Otherwise root.
if test "$lfr_root" = ""; then
  lfr_root=$lofar_top_srcdir;
  ]AC_CHECK_FILE([$lfr_root/$1/configure],
	         [lfr_var=yes],	[lfr_var=no])[
  if test $lfr_var = no; then
    lfr_root=$lofar_root;
  fi
else
  # Take version as given. Expand a possible tilde.
  # Add /lofar if only a 'symbolic' version name is given.
  case "$lfr_root" in
  root)
    lfr_root=$lofar_root;
    ;;
  ~*)
    lfr_root=`echo $lfr_root | sed -e "s%~%$HOME%"`;
    ;;
  */*)
    ;;
  *)
    lfr_root=/home/lofar/$lfr_root;
    ;;
  esac
fi
# Form the include directory (is src directory of package).
lfr_package_include=$lfr_root/$1;

# Add compiler type to variant if needed.
if test "$lfr_variant" != ""; then
  case "$lfr_variant" in
  *_*)
    ;;
  *)
    lfr_variant=${lofar_compiler}_$lfr_variant;
    ;;
  esac
fi

# Now get the library.
# If explicitly given, there is no problem at all.
if test "$lfr_package_libdir" = ""; then
  # If root used is the default one, also take variant from there.
  if test $lfr_root = $lofar_root; then
    lfr_package_libdir=$lfr_root/$1/build/$lofar_variant;
  else
    lfr_lib=$lfr_curwd;
    # The sources are from the user's tree, so find build area there as well.
    # Try to guess where the package library directory is located.
    # pwd gives the current build directory, which can be something
    # like   something/build/variant/package
    # or     something/package/build/variant
    # It simply replaces package by the actual package name in S1.
    if test "$lfr_variant" != ""; then
      lfr_curvar=`pwd | sed -e "s%.*/build/%%" | sed -e "s%/.*%%g"`;
      lfr_lib=`echo $lfr_lib | sed -e "s%/$lfr_curvar%/lfr_variant%"`
    fi
    lfr_pkg=`echo $lfr_srcdir | sed -e "s%.*/LOFAR/%%"`
    lfr_package_libdir=`echo $lfr_lib | sed -e "s%/$lfr_pkg%/$1%"`
  fi
fi

## Check if the build directory is valid.
## The library might not be there yet, but it must have been configured,
## so a libtool should be there.
##
## Check for Makefile.am header file in src dir.
##
  if test $lfr_option != 2; then
    ]AC_CHECK_FILE([$lfr_package_libdir/libtool],
			[lfr_cv_lib_package=yes],
			[lfr_cv_lib_package=no])
  [else
    lfr_cv_lib_package=yes;
  fi
]AC_CHECK_FILE([$lfr_package_include/src/Makefile.am],
			[lfr_cv_hdr_package=yes],
			[lfr_cv_hdr_package=no])dnl
[
if test $lfr_cv_hdr_package = yes  &&  test $lfr_cv_lib_package = yes; then
  # Turn possible relative paths into absolute paths, because
  # relative paths can miss some .. parts.
  lfr_package_include=`cd $lfr_package_include && pwd`

  # Two new variables for use in Makefile.am's
  ]LOFAR_PKG_LIB[_top_srcdir="$lfr_package_include"

  if test $lfr_option != 2; then
    lfr_package_libdir=`cd $lfr_package_libdir && pwd`
    ]LOFAR_PKG_LIB[_top_builddir="$lfr_package_libdir"
    LDFLAGS="$LDFLAGS -L$lfr_package_libdir/src"
    LIBS="$LIBS -l"]LOFAR_PKG_LIB[
  fi

  # Create symlink to the source and build directory
  # Do the same (if needed recursively) for all packages used by this package.
  rm -f libnames_depend
  touch libnames_depend
  $lofar_sharedir/makepkglinks $1 $lfr_package_include $lfr_package_libdir pkginc pkgbldinc libnames_depend $lfr_option 0
  lfr_depend=`cat libnames_depend`
  rm libnames_depend
  LOFAR_DEPEND="$LOFAR_DEPEND $lfr_depend"
]
dnl
AC_SUBST(LIBS)dnl
AC_SUBST([LOFAR_PKG_LIB][[_top_srcdir]])dnl
AC_SUBST([LOFAR_PKG_LIB][[_top_builddir]])dnl
AC_SUBST(LOFAR_DEPEND)dnl
dnl
dnl NOT NEEDED: AC_DEFINE(HAVE_LOFAR_PKG, 1, [Define if Package is installed])dnl
[
else
  if test $lfr_cv_hdr_package = no; then]
AC_MSG_ERROR([Could not find Makefile.am in $lfr_package_include])
[
    enable_package=no
  else]
AC_MSG_WARN([Could not find libtool in $lfr_package_libdir])
AC_MSG_ERROR([Probably package $1 has not been configured yet])
[
  fi
fi
]
dnl NOT NEEDED: AM_CONDITIONAL(HAVE_LOFAR_PKG, test "$enable_package" = "yes")
])
