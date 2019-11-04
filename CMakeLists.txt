# Meqtrees CMake Build File
project(meqtrees CXX C)

IF(DEFINED CMAKE_BUILD_TYPE)
   IF((CMAKE_BUILD_TYPE STREQUAL "Debug") OR (CMAKE_BUILD_TYPE STREQUAL "Release") OR (CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo") OR (CMAKE_BUILD_TYPE STREQUAL "MinSizeRel"))
      MESSAGE("-- Build type is defined as '${CMAKE_BUILD_TYPE}'")
   ELSE()
      SET(CMAKE_BUILD_TYPE "Release")   
      MESSAGE("-- Invalid option for BUILD TYPE, defaulted to '${CMAKE_BUILD_TYPE}' build")
   ENDIF()
ELSE()
   SET(CMAKE_BUILD_TYPE "Release")
   MESSAGE("-- Build type wasn't defined, defaulted to '${CMAKE_BUILD_TYPE}' build")
ENDIF()
IF(CMAKE_BUILD_TYPE STREQUAL "Debug")
  MESSAGE(WARNING "You are compiling the backend in debugging mode... things may be slower than usual. Overriding all optimizations to 'OFF'")
ENDIF()

# -- cmake setup info
cmake_minimum_required(VERSION 2.6)

# CUDA
find_package(CUDA 4.0)
set(CUDA_FOUND false)
if (CUDA_FOUND)
  message(" * CUDA ${CUDA_VERSION} was found")
  add_library( cudart STATIC IMPORTED )
  add_library( cutil64D STATIC IMPORTED )
  set(CUDA_NVCC_FLAGS -arch=sm_13 --ptxas-options -v)
else(CUDA_FOUND)
  message(" * CUDA not found -- CUDA support disabled. This support is still only experimental, do not be alarmed.")
  set (CUDA_TOOLKIT_INCLUDE "")
  add_definitions(-DSTRIP_CUDA)
endif(CUDA_FOUND)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_SOURCE_DIR}/cmake)
include(cmake/meqmacros.cmake)
include(cmake/mequtils.cmake)

option(ENABLE_PYTHON_3 "Enables support for Python 3.x" OFF)
if (NOT "${ENABLE_PYTHON_3}")
    message("-- Compiling backend against Python 2.7")
    message("-- If this is not the intended target specify the ENABLE_PYTHON_3 switch")
    set(PYREQ_VER 2.7)
    set(PYABI .cpython-27)
    find_package(PythonInterp ${PYREQ_VER} EXACT REQUIRED)
    find_package(PythonLibs ${PYREQ_VER} EXACT REQUIRED)
else(NOT "${ENABLE_PYTHON_3}")
    message("-- Compiling backend against Python 3.x")
    set(PYREQ_VER 3.0)
    set(PYABI .cpython-30)
    find_package(PythonInterp ${PYREQ_VER} REQUIRED)    
    find_package(PythonLibs ${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR} EXACT REQUIRED)
endif(NOT "${ENABLE_PYTHON_3}")

include (FindPythonInterp)
include (FindPythonLibs)
include(cmake/SetPythonPackagesDir.cmake)

# had to add this to get working on Ubuntu 11.10 g{cc/++}4.6 since the include directory structure seems to have changed
#include_directories(/usr/include/i386-linux-gnu/)

# options and defaults
set( BUILD_SHARED_LIBS TRUE )

if(NOT LIBRARY_INSTALL_DIR )
    set( LIBRARY_INSTALL_DIR lib )
endif(NOT LIBRARY_INSTALL_DIR )

if(NOT MEQTREES_INSTALL_DIR )
    set( MEQTREES_INSTALL_DIR "${LIBRARY_INSTALL_DIR}/meqtrees" )
endif(NOT MEQTREES_INSTALL_DIR )

if(NOT PYTHON_INSTALL_DIR )
    set( PYTHON_INSTALL_DIR "${PYTHON_PACKAGES_DIR}/Timba" )
endif(NOT PYTHON_INSTALL_DIR )

if(NOT INCLUDE_INSTALL_DIR )
    set( INCLUDE_INSTALL_DIR "include/meqtrees" )
endif(NOT INCLUDE_INSTALL_DIR )

if(NOT ICON_INSTALL_DIR )
    set( ICON_INSTALL_DIR "${PYTHON_INSTALL_DIR}/icons" )
endif(NOT ICON_INSTALL_DIR )

# project version
set( ${PROJECT_NAME}_MAJOR_VERSION 1 )
set( ${PROJECT_NAME}_MINOR_VERSION 6 )
set( ${PROJECT_NAME}_PATCH_LEVEL 0 )

# -- dependencies
set(dependencies
                 Blitz
                 PythonLibs
                 CasaCore
                 DBM
                 WcsLib
                 FFTW3
                 CfitsIO
                 Threads
                 PythonNumpy
)
# alternative builds
if(USE_MPI)
    list(APPEND dependencies MPI)
endif(USE_MPI)

PACKAGE_DEPENDENCIES( ${dependencies} )
if(DBM_FLAGS)
  add_definitions(${DBM_FLAGS})
endif(DBM_FLAGS)

if(CASACORE_FOUND)
    add_definitions(-DHAVE_AIPSPP)
endif(CASACORE_FOUND)

# -- compiler defaults
add_definitions(-DUSE_STD_COMPLEX -DMAKE_LOFAR_SYMBOLS_GLOBAL -DUSE_THREADS -fPIC)
SET(CPP_PLATFORM_LIBS ${CMAKE_THREAD_LIBS_INIT})
if(CMAKE_COMPILER_IS_GNUCC)
    add_definitions(-Wno-deprecated -D_GNU_SOURCE -Wno-unknown-pragmas -std=c++17 -Wfatal-errors)
    list(APPEND CPP_PLATFORM_LIBS util dl)
endif(CMAKE_COMPILER_IS_GNUCC)
IF(APPLE)
    add_definitions(-DDARWIN)
ENDIF(APPLE)

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
