INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH} )
MEQPACKAGE( OCTOPython OCTOPUSSY DMI TimBase )
set(octopython_include
        src/AID-OctoPython.h
        src/OctoPython.h
        src/TID-OctoPython.h
        src/TypeIter-OctoPython.h
)
INCLUDE_SETUP(OCTOPython ${octopython_include})

set(src 
        src/AID-OctoPython-Registry.cc
        src/DataConv.cc
        src/LazyObjRef.cc
        src/octopython.cc
        src/ProxyWPObject.cc
        src/ThreadCond.cc
)
add_library(octopython ${src})
install(TARGETS octopython DESTINATION ${LIBRARY_INSTALL_DIR})
install(FILES src/version_info/__init__.py DESTINATION ${PYTHON_INSTALL_DIR}/version_info)
MEQPACKAGE_ADD_LIBRARIES(octopython ${PYTHON_LIBRARIES})
