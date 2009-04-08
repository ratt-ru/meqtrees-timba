# - Find wcslib
# Find the native FFTW3 includes and library
#
#  FFTW3_INCLUDE_DIR - where to find wcslib.h, etc.
#  FFTW3_LIBRARIES   - List of libraries when using wcslib.
#  FFTW3_FOUND       - True if wcslib found.

IF (FFTW3_INCLUDE_DIR)
    # Already in cache, be silent
    SET(FFTW3_FIND_QUIETLY TRUE)
ENDIF (FFTW3_INCLUDE_DIR)

FIND_PATH(FFTW3_INCLUDE_DIR fftw3.h )

SET(FFTW3_NAMES 
    fftw3l_threads
    fftw3
    fftw3l
    )
FOREACH( lib ${FFTW3_NAMES} )
FIND_LIBRARY(FFTW3_LIBRARY_${lib} NAMES ${lib} )
    LIST(APPEND FFTW3_LIBRARIES ${FFTW3_LIBRARY_${lib}})
ENDFOREACH(lib)

# handle the QUIETLY and REQUIRED arguments and set FFTW3_FOUND to TRUE if.
# all listed variables are TRUE
INCLUDE(FindPackageHandleCompat)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(FFTW3 DEFAULT_MSG FFTW3_LIBRARIES FFTW3_INCLUDE_DIR)

IF(NOT FFTW3_FOUND)
    SET( FFTW3_LIBRARIES )
ENDIF(NOT FFTW3_FOUND)

MARK_AS_ADVANCED( FFTW3_LIBRARIES FFTW3_INCLUDE_DIR )

