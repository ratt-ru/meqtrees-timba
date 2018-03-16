# - Find wcslib
# Find the native DBM includes and library
#
#  DBM_INCLUDE_DIR - where to find wcslib.h, etc.
#  DBM_LIBRARIES   - List of libraries when using wcslib.
#  DBM_FOUND       - True if wcslib found.
#  DBM_TYPE        - type of library found first in the list (QDBMS,GDBMS)
#  DBM_FLAGS       - flags to indicate type

IF (DBM_INCLUDE_DIR)
    # Already in cache, be silent
    SET(DBM_FIND_QUIETLY TRUE)
ENDIF (DBM_INCLUDE_DIR)

SET(QDBM_NAMES 
    qdbm
    )

# look for QDBM
SET(DBM_TYPE QDBM)
FIND_PATH(DBM_INCLUDE_DIR qdbm/depot.h)
FOREACH( lib ${QDBM_NAMES} )
    FIND_LIBRARY(DBM_LIBRARY_${lib} NAMES ${lib} )
    IF(DBM_LIBRARY_${lib})
        LIST(APPEND DBM_LIBRARIES ${DBM_LIBRARY_${lib}})
    ENDIF(DBM_LIBRARY_${lib})
ENDFOREACH(lib)


# handle the QUIETLY and REQUIRED arguments and set DBM_FOUND to TRUE if.
# all listed variables are TRUE
INCLUDE(FindPackageHandleCompat)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(DBM DEFAULT_MSG DBM_LIBRARIES DBM_INCLUDE_DIR)

IF(NOT DBM_FOUND)
    SET( DBM_LIBRARIES )
    SET( DBM_TYPE )
    SET( DBM_FLAGS )
ELSE(NOT DBM_FOUND)
    SET( DBM_FLAGS -DHAVE_${DBM_TYPE} )
ENDIF(NOT DBM_FOUND)

MARK_AS_ADVANCED( DBM_LIBRARIES DBM_INCLUDE_DIR DBM_TYPE )

