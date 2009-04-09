# Usage:
#   INCLUDE_SETUP( Subdirectory fileList )
#
# Description:
#   For each file in the fileList a copy is made in BUILD_INCLUDE_DIR/Subdirectory
#   Dependency targets are set for SubDirectory/filename
#
SET(BUILD_INCLUDE_DIR ${CMAKE_BINARY_DIR}/include)
FILE(MAKE_DIRECTORY ${BUILD_INCLUDE_DIR})
INCLUDE_DIRECTORIES(${BUILD_INCLUDE_DIR})

MACRO(INCLUDE_SETUP dest)
  FILE(MAKE_DIRECTORY ${BUILD_INCLUDE_DIR}/${dest})
  FOREACH(file ${ARGN})
      GET_FILENAME_COMPONENT(filename ${file} NAME )
      SET(in_file ${CMAKE_CURRENT_BINARY_DIR}/${dest}_${filename})
      SET(out_file ${BUILD_INCLUDE_DIR}/${dest}/${filename})
      FILE(WRITE ${in_file}
          "#include \"${CMAKE_CURRENT_SOURCE_DIR}/${file}\"\n"
          )
      CONFIGURE_FILE(${in_file} ${out_file} COPYONLY)
      INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/${file} DESTINATION ${INCLUDE_INSTALL_DIR}/${dest} )
  ENDFOREACH(file)
ENDMACRO(INCLUDE_SETUP dest)
#
# create the lofar_config.h
# First argument is tha Lofar package name, subsequent are Lofar package dependencies
MACRO(LOFAR_SETUP packageName)
    string(TOUPPER ${packageName} package)
    INCLUDE_DIRECTORIES(${CMAKE_CURRENT_BINARY_DIR})
    set(LOFAR_CONFIG_H ${CMAKE_CURRENT_BINARY_DIR}/lofar_config.h.gen)
    FILE(WRITE "${LOFAR_CONFIG_H}"
        "#ifndef LOFAR_CONFIG_H\n"
        "#define LOFAR_CONFIG_H\n"
        "#include <config.h>\n"
        "#define HAVE_LOFAR_${package} 1\n"
        )
    FOREACH(pack ${ARGN})
        string(TOUPPER ${pack} file)
        FILE(APPEND "${LOFAR_CONFIG_H}"
            "#if !defined(HAVE_LOFAR_${file})\n"
            "#define HAVE_LOFAR_${file} 1\n"
            "#endif\n"
            )
    ENDFOREACH(pack)
    FILE(APPEND "${LOFAR_CONFIG_H}"
        "#endif\n"
        )
    SET_SOURCE_FILES_PROPERTIES(${CMAKE_CURRENT_BINARY_DIR}/lofar_config.h PROPERTIES GENERATED 1)
    CONFIGURE_FILE("${LOFAR_CONFIG_H}" "${CMAKE_CURRENT_BINARY_DIR}/lofar_config.h" COPYONLY)
ENDMACRO(LOFAR_SETUP)

#
# Load in Package Dependencies and create the config.h
#

# -- this from the existing config.h - not sure whats needed
INCLUDE (CheckIncludeFiles)
INCLUDE(TestBigEndian)
TEST_BIG_ENDIAN(WORDS_BIGENDIAN)
CHECK_INCLUDE_FILES(malloc.h HAVE_MALLOC_H)
CHECK_INCLUDE_FILES("sys/param.h;sys/mount.h" HAVE_SYS_MOUNT_H)
CHECK_INCLUDE_FILES(dlfcn.h HAVE_DLFCN_H)
CHECK_INCLUDE_FILES(stdint.h HAVE_STDINT_H)
CHECK_INCLUDE_FILES(stdlib.h HAVE_STDLIB_H)
CHECK_INCLUDE_FILES(strings.h HAVE_STRINGS_H)
CHECK_INCLUDE_FILES("string.h" HAVE_STRING_H)
CHECK_INCLUDE_FILES("sys/stat.h" HAVE_SYS_STAT_H)
CHECK_INCLUDE_FILES("sys/types.h" HAVE_SYS_TYPES_H)
CHECK_INCLUDE_FILES( unistd.h HAVE_UNISTD_H)
CHECK_INCLUDE_FILES( memory.h HAVE_MEMORY_H)

MACRO( PACKAGE_DEPENDENCIES )
    # add the default configurations
    # generate a config_in_file to avoid 
    # always generating causing unnessasary rebuilds
    set(config_header "${BUILD_INCLUDE_DIR}/config.h")
    set(config_in_file "${CMAKE_CURRENT_BINARY_DIR}/config.h.in")
    CONFIGURE_FILE(${CMAKE_SOURCE_DIR}/cmake/config.h.in "${config_in_file}")
    # add specific packages
    FOREACH(pack ${ARGN})
        #message( "Looking for Package ${pack}" )
        string(TOUPPER ${pack} packvar)
        FIND_PACKAGE(${pack})
        IF(${packvar}_FOUND)
            FILE(APPEND ${config_in_file}
                "#define HAVE_${packvar} 1\n"
            )
        ENDIF(${packvar}_FOUND)
    ENDFOREACH(pack)
    CONFIGURE_FILE(${config_in_file} "${config_header}")
ENDMACRO( PACKAGE_DEPENDENCIES )

#
# Define a directory as a MEQPACKAGE( packageName meqpackage_dependencies )
# 

MACRO( MEQPACKAGE_ADD_LIBRARIES )
    IF(MEQPACKAGE_CURRENT)
        LIST(INSERT MEQPACKAGE_LIBRARIES 0 ${ARGN})
        LIST(INSERT MEQPACKAGE_${MEQPACKAGE_CURRENT}_LIBS 0 ${ARGN})
        FILE(APPEND ${MEQPACKAGE_FILE}
            "LIST(INSERT MEQPACKAGE_${MEQPACKAGE_CURRENT}_LIBS 0 ${ARGN})\n"
            )
    ELSE(MEQPACKAGE_CURRENT)
        MESSAGE("Error: MEQPACKAGE_ADD_LIBRARIES specified outside of a MEQPACKAGE context")
    ENDIF(MEQPACKAGE_CURRENT)
ENDMACRO( MEQPACKAGE_ADD_LIBRARIES )

#
# private macro to generate the MEQPACKAGE_LIBRARIES variable
#
MACRO( MEQPACKAGE_GET_LIBS package )
    IF(NOT MEQPACKAGE_${package}_ADDED)
    FOREACH(pack ${MEQPACKAGE_${package}_DEPS} )
        MEQPACKAGE_GET_LIBS(${pack})
    ENDFOREACH(pack)
    LIST(INSERT MEQPACKAGE_LIBRARIES 0 ${MEQPACKAGE_${package}_LIBS})
    SET(MEQPACKAGE_${package}_ADDED TRUE)
    ENDIF(NOT MEQPACKAGE_${package}_ADDED)
ENDMACRO( MEQPACKAGE_GET_LIBS )

SET(MEQPACKAGE_WORK_DIR ${CMAKE_BINARY_DIR}/_meqpackages)
mark_as_advanced(MEQPACKAGE_CURRENT)
mark_as_advanced(MEQPACKAGE_WORK_DIR)
mark_as_advanced(MEQPACKAGE_LIBRARIES)

FILE(MAKE_DIRECTORY ${MEQPACKAGE_WORK_DIR})
#
# macro to generate requirements for a MEQPACKAGE
# and load dependencies
#
MACRO( MEQPACKAGE package )
    set(MEQPACKAGE_CURRENT "${package}")
    set(MEQPACKAGE_${package}_DEPS ${ARGN})
    IF(MEQPACKAGE_${package}_DEPS)
        LIST(REVERSE MEQPACKAGE_${package}_DEPS)
    ENDIF(MEQPACKAGE_${package}_DEPS)
    set(MEQPACKAGE_FILE "${MEQPACKAGE_WORK_DIR}/${package}.cmake")
    FILE(WRITE ${MEQPACKAGE_FILE}
        "# Autogenerated file for the package : ${package} - do not edit\n"
        "IF(MEQPACKAGE_${package}_LIBS)\n"
        "RETURN()\n"
        "ENDIF(MEQPACKAGE_${package}_LIBS)\n"
        "LIST(APPEND LOFAR_PACKAGES ${package} ${ARGN})\n"
        )
    IF(MEQPACKAGE_${package}_DEPS)
        FILE(APPEND ${MEQPACKAGE_FILE}
            "SET(MEQPACKAGE_${package}_DEPS ${MEQPACKAGE_${package}_DEPS})\n"
            )
    ENDIF(MEQPACKAGE_${package}_DEPS)
    # -- all include directories defined before the macro call are exported
    IF(COMMAND GET_PROPERTY)
        get_property( includes DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY INCLUDE_DIRECTORIES )
    ELSE(COMMAND GET_PROPERTY)
        # -- cmake 2.4 compatablity, just include everything
        set(includes ${CMAKE_INCLUDE_PATH})
    ENDIF(COMMAND GET_PROPERTY)
    FOREACH(inc ${includes})
        FILE(APPEND ${MEQPACKAGE_FILE}
            "include_directories(${inc})\n"
            )
    ENDFOREACH(inc)
    FOREACH(pack ${ARGN})
        FILE(APPEND ${MEQPACKAGE_FILE}
            "include( ${MEQPACKAGE_WORK_DIR}/${pack}.cmake )\n"
            )
    ENDFOREACH(pack)
    FOREACH(dep ${MEQPACKAGE_${package}_DEPS} )
        include(${MEQPACKAGE_WORK_DIR}/${dep}.cmake)
        MEQPACKAGE_GET_LIBS(${dep})
    ENDFOREACH(dep)
    IF(MEQPACKAGE_LIBRARIES)
    LIST(REMOVE_DUPLICATES MEQPACKAGE_LIBRARIES)
    ENDIF(MEQPACKAGE_LIBRARIES)
    FILE(APPEND ${MEQPACKAGE_FILE}
        "IF(LOFAR_PACKAGES)\n"
        "LIST(REMOVE_DUPLICATES LOFAR_PACKAGES)\n"
        "ENDIF(LOFAR_PACKAGES)\n"
        )
    LOFAR_SETUP("${package}" ${LOFAR_PACKAGES})
ENDMACRO( MEQPACKAGE )

MACRO( MEQPACKAGE_OLD package )
    set(MEQPACKAGE_CURRENT "${package}")
    set(MEQPACKAGE_${package}_DEPS ${ARGN})
    IF(MEQPACKAGE_${package}_DEPS)
        LIST(REVERSE MEQPACKAGE_${package}_DEPS)
    ENDIF(MEQPACKAGE_${package}_DEPS)
    set(MEQPACKAGE_FILE "${MEQPACKAGE_WORK_DIR}/${package}.cmake")
    FILE(WRITE ${MEQPACKAGE_FILE}
        "# Autogenerated file for the package : ${package} - do not edit\n"
        "IF(MEQPACKAGE_${package}_LIBS)\n"
        "RETURN()\n"
        "ENDIF(MEQPACKAGE_${package}_LIBS)\n"
        "LIST(APPEND LOFAR_PACKAGES ${package} ${ARGN})\n"
        )
    IF(MEQPACKAGE_${package}_DEPS)
        FILE(APPEND ${MEQPACKAGE_FILE}
            "SET(MEQPACKAGE_${package}_DEPS ${MEQPACKAGE_${package}_DEPS})\n"
            )
    ENDIF(MEQPACKAGE_${package}_DEPS)
    # -- all include directories defined before the macro call are exported
    get_property( includes DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY INCLUDE_DIRECTORIES )
    FOREACH(inc ${includes})
        FILE(APPEND ${MEQPACKAGE_FILE}
            "include_directories(${inc})\n"
            )
    ENDFOREACH(inc)
    FOREACH(pack ${ARGN})
        FILE(APPEND ${MEQPACKAGE_FILE}
            "include( ${MEQPACKAGE_WORK_DIR}/${pack}.cmake )\n"
            )
    ENDFOREACH(pack)
    FOREACH(dep ${MEQPACKAGE_${package}_DEPS} )
        include(${MEQPACKAGE_WORK_DIR}/${dep})
        MEQPACKAGE_GET_LIBS(${dep})
    ENDFOREACH(dep)
    IF(MEQPACKAGE_LIBRARIES)
    LIST(REMOVE_DUPLICATES MEQPACKAGE_LIBRARIES)
    ENDIF(MEQPACKAGE_LIBRARIES)
    FILE(APPEND ${MEQPACKAGE_FILE}
        "IF(LOFAR_PACKAGES)\n"
        "LIST(REMOVE_DUPLICATES LOFAR_PACKAGES)\n"
        "ENDIF(LOFAR_PACKAGES)\n"
        )
    LOFAR_SETUP("${package}" ${LOFAR_PACKAGES})
ENDMACRO( MEQPACKAGE_OLD )


