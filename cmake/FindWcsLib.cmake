# - Find wcslib
# Find the native WCSLIB includes and library
#
#  WCSLIB_INCLUDE_DIR - where to find wcslib.h, etc.
#  WCSLIB_LIBRARIES   - List of libraries when using wcslib.
#  WCSLIB_FOUND       - True if wcslib found.

IF (WCSLIB_INCLUDE_DIR)
    # Already in cache, be silent
    SET(WCSLIB_FIND_QUIETLY TRUE)
ENDIF (WCSLIB_INCLUDE_DIR)

FIND_PATH(WCSLIB_INCLUDE_DIR wcslib)

SET(WCSLIB_NAMES 
    #    pgsbox
    wcs
    )
FOREACH( lib ${WCSLIB_NAMES} )
FIND_LIBRARY(WCSLIB_LIBRARY_${lib} NAMES ${lib} )
    LIST(APPEND WCSLIB_LIBRARIES ${WCSLIB_LIBRARY_${lib}})
ENDFOREACH(lib)

# handle the QUIETLY and REQUIRED arguments and set WCSLIB_FOUND to TRUE if.
# all listed variables are TRUE
INCLUDE(FindPackageHandleCompat)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(WCSLIB DEFAULT_MSG WCSLIB_LIBRARIES WCSLIB_INCLUDE_DIR)

IF(NOT WCSLIB_FOUND)
    SET( WCSLIB_LIBRARIES )
ENDIF(NOT WCSLIB_FOUND)

MARK_AS_ADVANCED( WCSLIB_LIBRARIES WCSLIB_INCLUDE_DIR )

