# - Find blitz
# Find the native BLITZ includes and library
#
#  BLITZ_INCLUDE_DIR - where to find blitz.h, etc.
#  BLITZ_LIBRARY_DIR - where to find blitz libraries.
#  BLITZ_LIBRARIES   - List of libraries when using blitz.
#  BLITZ_FOUND       - True if blitz found.


IF (BLITZ_INCLUDE_DIR)
    # Already in cache, be silent
    SET(BLITZ_FIND_QUIETLY TRUE)
ENDIF (BLITZ_INCLUDE_DIR)

FIND_PATH(BLITZ_INCLUDE_DIR blitz/blitz.h PATHS /opt/mpp/blitz/0.9/inlcude )
FIND_PATH(BLITZ_INCLUDE_DIR2 blitz/gnu/bzconfig.h PATHS ${BLITZ_INCLUDE_DIR} /usr/lib64/blitz/include /usr/lib/blitz/include DOC "some distros have moved platform specifc includes into a separate directory")
IF(NOT ${BLITZ_INCLUDE_DIR2} MATCHES ${BLITZ_INCLUDE_DIR} )
message("Found BLITZ include files insame dir")
      set(BLITZ_INCLUDE_DIR ${BLITZ_INCLUDE_DIR} ${BLITZ_INCLUDE_DIR2})
ENDIF(NOT ${BLITZ_INCLUDE_DIR2} MATCHES ${BLITZ_INCLUDE_DIR} )
SET(BLITZ_NAMES blitz)
FIND_LIBRARY(BLITZ_LIBRARY NAMES ${BLITZ_NAMES} PATHS $ENV{BLITZ_LIBRARY_DIR} ${BLITZ_LIBRARY_DIR} /opt/mpp/blitz/0.9/lib )

# handle the QUIETLY and REQUIRED arguments and set BLITZ_FOUND to TRUE if.
# all listed variables are TRUE
INCLUDE(FindPackageHandleCompat)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(BLITZ DEFAULT_MSG BLITZ_LIBRARY BLITZ_INCLUDE_DIR BLITZ_INCLUDE_DIR2)

IF(BLITZ_FOUND)
    SET( BLITZ_LIBRARIES ${BLITZ_LIBRARY} )
ELSE(BLITZ_FOUND)
    SET( BLITZ_LIBRARIES )
ENDIF(BLITZ_FOUND)

MARK_AS_ADVANCED( BLITZ_LIBRARY BLITZ_INCLUDE_DIR  BLITZ_INCLUDE_DIR2 )

