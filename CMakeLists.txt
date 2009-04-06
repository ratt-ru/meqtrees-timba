# Meqtrees CMake Build File
project(meqtrees)
list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_SOURCE_DIR}/cmake)
include(cmake/meqmacros.cmake)
include(cmake/mequtils.cmake)
cmake_minimum_required(VERSION 2.6)

# options and defaults
SET( BUILD_SHARED_LIBS TRUE )

IF(NOT LIBRARY_INSTALL_DIR )
    SET( LIBRARY_INSTALL_DIR lib )
ENDIF(NOT LIBRARY_INSTALL_DIR )

IF(NOT MEQTREES_INSTALL_DIR )
    SET( MEQTREES_INSTALL_DIR "${LIBRARY_INSTALL_DIR}/meqtrees" )
ENDIF(NOT MEQTREES_INSTALL_DIR )

IF(NOT PYTHON_INSTALL_DIR )
    SET( PYTHON_INSTALL_DIR "${MEQTREES_INSTALL_DIR}/Timba" )
ENDIF(NOT PYTHON_INSTALL_DIR )

IF(NOT ICON_INSTALL_DIR )
    SET( ICON_INSTALL_DIR "${MEQTREES_INSTALL_DIR}/icons" )
ENDIF(NOT ICON_INSTALL_DIR )

# project version
SET( ${PROJECT_NAME}_MAJOR_VERSION 1 )
SET( ${PROJECT_NAME}_MINOR_VERSION 1 )
SET( ${PROJECT_NAME}_PATCH_LEVEL 0 )

# -- dependencies
set(dependencies
                 Blitz
                 PythonLibs
                 CasaCore
                 WcsLib
                 FFTW3
                 CfitsIO
                 Threads
)
PACKAGE_DEPENDENCIES( ${dependencies} )

IF(CASACORE_FOUND)
    ADD_DEFINITIONS(-DHAVE_AIPSPP)
ENDIF(CASACORE_FOUND)

# -- compiler defaults
ADD_DEFINITIONS(-DMAKE_LOFAR_SYMBOLS_GLOBAL -DUSE_THREADS)
IF(CMAKE_COMPILER_IS_GNUCC)
ADD_DEFINITIONS(-Wno-deprecated -D_GNU_SOURCE  -Wno-unknown-pragmas)
ENDIF(CMAKE_COMPILER_IS_GNUCC)

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
