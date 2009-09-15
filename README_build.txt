MeqTrees and the CMAKE Build System
===================================

CMake is a platform independent build system, that allows 
out of source code builds.

Full cmake documentation can be found at:
www.cmake.org


Simple Install
==============
Note that the CMAKE_INSTALL_PREFIX variable will define the relative location 
where the install target will put files. On unix platforms this defaults to "/usr/local".

Step 1:
      create a directory for the build to take place
      > mkdir meqtrees_build; cd meqtrees_build
Step 2:
      from this build directory run cmake to create the platform specific make files
      > cmake PATH_TO_SRC
Step 3:
      run the platform specific make command. 
      e.g. unix based systems
      > make install

      e.g. windows based systems (MSVC)
      > nmake install

External Dependencies
=====================
CMake attempts to find all the external dependencies in the project automatically.
If you have these pacakges installed in an unusual place you may have to specify the locations
through cmake variables. The variable is dependent on the package - for the names, look in the 
relevant Find<packageName>.cmake files found in the cmake directory of the src code and the
system cmake module directory (usually /usr/share/cmake/Modules)

The list of external dependency packages are specified by the dependencies variable set
in the top level CMakeList.txt file.

Alternative Builds
==================
Various alternative builds are available. Activate them by setting the 
appropriate Cmake variable:

  Variable                   Description
  ---------------------------------------------------
  USE_MPI                  | Use the mpi parrallelisation library
  USE_DBM                  | Use a database management system



Setting CMake Variables
=======================
Various options and configurations are available by setting CMake variables
CMake variables can be set by calling cmake with the -D option
e.g.
         cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_CXX_COMPILER=g++-4.2 <SRC_DIRECTORY>

Build options
--------------

  Variable                              | Function
  ------------------------------------------------------------
    CMAKE_BUILD_TYPE=DEBUG|RELEASE      |  build debug or release versions 
                                        |
    CMAKE_CXX_FLAGS=                    |  Extra flags to use when compiling C++ source files.
                                        |
    LIBRARY_INSTALL_DIR=                |  specify location for meqtrees libraries
                                        |  ( default: CMAKE_INSTALL_PREFIX/lib )
                                        |
    MEQTREES_INSTALL_DIR=               |  specify location for meqtrees libraries and other resources
                                        |  ( default: LIBRARY_INSTALL_DIR/meqtrees )
                                        |
    ICON_INSTALL_DIR=                   |  directory to install icons (default: MEQTREES_INSTALL_DIR/icons )
                                        |
    PYTHON_INSTALL_DIR=                 |  installation dir for meqtrees specific python scripts
                                        |  (default: MEQTREES_INSTALL_DIR/Timba )

cmake specifc variables can be found here: http://www.cmake.org/Wiki/CMake_Useful_Variables

Convenience Configuration Script
================================
A script has been provided in the Tools/Build directory for convenience for the most common
use cases. The function of the script is to create build product locations 
and configure cmake appropriately.

e.g. To create a debug build 
> Tools/Build/bootstrap_cmake debug

e.g. To create an optimised build
> Tools/Build/bootstrap_cmake release

-------------------------------------- For Developers -----------------------------------------------------------------
MEQTREES Specific MACROS
========================
A number of convenience Macros are provided to ease the creation of MeqTrees packages.
Here is a quick overview of the main functionality, refer to the cmake/meqmacros.cmake
for full information.

The MEQPACKAGE
--------------
Specify the contents are a MeqPackage and the primary dependencies on other MeqTrees Packages
This will ensure all the INCLUDE_PATHS are correct and the MEQPACKAGE_LIBRARIES variable
will contain all the required variables. It will also genertate the correct lofar_config.h file.

e.g. CMakeLists.txt for a simple MEQPACKAGE

    # Exported Paths for External Dependencies
    INCLUDE_DIRECTORIES(${AnExternalPackage_INCLUDE_DIR})
    INCLUDE_DIRECTORIES(${AnotherExternalPackage_INCLUDE_DIR})                      # These INCLUDE paths will be exported to dependent Meq Packages

    MEQPACKAGE(MyPackageName meqPackageDependenyA meqPackageDependencyB)            # declares the MeqPacake "MyPackageName" and its primary dependencies

    # Non-Exported Paths should be specified after the MEQPACKAGE macro
    INCLUDE_DIRECTORIES(${ADependencyNotExported_INCLUDE_DIR})                      # This INCLUDE directory will not be exported - local to this package only

    # Export Header files myHeader.h and myHeader2.h to the MyPackage directory
    INCLUDE_SETUP(MyPackage myHeader.h myHeader2.h)

    # mark libraries for export to other MeqPackages
    # with the MEQPACKAGE_ADD_LIBRARIES macro
    MEQPACKAGE_ADD_LIBRARIES(myPackageLib ${AnExternalPackage_LIB_DIR} ${AnotherExternalPackage_LIB_DIR})

