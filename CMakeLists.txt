# Meqtrees CMake Build File
project(meqtrees CXX C)

# -- cmake setup info
cmake_minimum_required(VERSION 2.6)
list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_SOURCE_DIR}/cmake)
include(cmake/meqmacros.cmake)
include(cmake/mequtils.cmake)

# options and defaults
set( BUILD_SHARED_LIBS TRUE )

if(NOT LIBRARY_INSTALL_DIR )
    set( LIBRARY_INSTALL_DIR lib )
endif(NOT LIBRARY_INSTALL_DIR )

if(NOT MEQTREES_INSTALL_DIR )
    set( MEQTREES_INSTALL_DIR "${LIBRARY_INSTALL_DIR}/meqtrees" )
endif(NOT MEQTREES_INSTALL_DIR )

if(NOT PYTHON_INSTALL_DIR )
    set( PYTHON_INSTALL_DIR "${MEQTREES_INSTALL_DIR}/Timba" )
endif(NOT PYTHON_INSTALL_DIR )

if(NOT INCLUDE_INSTALL_DIR )
    set( INCLUDE_INSTALL_DIR "include/meqtrees" )
endif(NOT INCLUDE_INSTALL_DIR )

if(NOT ICON_INSTALL_DIR )
    set( ICON_INSTALL_DIR "${MEQTREES_INSTALL_DIR}/icons" )
endif(NOT ICON_INSTALL_DIR )

# project version
set( ${PROJECT_NAME}_MAJOR_VERSION 1 )
set( ${PROJECT_NAME}_MINOR_VERSION 1 )
set( ${PROJECT_NAME}_PATCH_LEVEL 0 )

# -- dependencies
set(dependencies
                 Blitz
                 PythonLibs
                 CasaCore
                 WcsLib
                 FFTW3
                 CfitsIO
                 Threads
                 PythonNumpy
)
PACKAGE_DEPENDENCIES( ${dependencies} )

if(CASACORE_FOUND)
    add_definitions(-DHAVE_AIPSPP)
endif(CASACORE_FOUND)

# -- compiler defaults
add_definitions(-DUSE_STD_COMPLEX -DMAKE_LOFAR_SYMBOLS_GLOBAL -DUSE_THREADS)
SET(CPP_PLATFORM_LIBS)
if(CMAKE_COMPILER_IS_GNUCC)
    add_definitions(-Wno-deprecated -D_GNU_SOURCE -Wno-unknown-pragmas)
    SET(CPP_PLATFORM_LIBS util dl)
endif(CMAKE_COMPILER_IS_GNUCC)

# -- sub modules
add_subdirectory(TimBase)
add_subdirectory(DMI)
add_subdirectory(OCTOPUSSY)
add_subdirectory(OCTOPython)
add_subdirectory(MEQ)
add_subdirectory(VisCube)
add_subdirectory(MeqMPI)
add_subdirectory(MeqNodes)
add_subdirectory(AppAgent)
add_subdirectory(MeqServer)
add_subdirectory(PyApps)
#add_subdirectory(PyParmDB)
#add_subdirectory(Tests)
