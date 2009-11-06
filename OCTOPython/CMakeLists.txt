INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH} ${PYTHON_NUMPY_INCLUDE_DIR} )
MEQPACKAGE( OCTOPython OCTOPUSSY DMI TimBase )
set(octopython_include
        src/AID-OctoPython.h
        src/OctoPython.h
        src/TID-OctoPython.h
        src/TypeIter-OctoPython.h
)
INCLUDE_SETUP(OCTOPython ${octopython_include} )

set(src
        src/AID-OctoPython-Registry.cc
        src/DataConv.cc
        src/LazyObjRef.cc
        src/octopython.cc
        src/ProxyWPObject.cc
        src/ThreadCond.cc
)
add_library(octopython SHARED ${src})
set_target_properties(octopython PROPERTIES PREFIX "")
target_link_libraries(octopython ${MEQPACKAGE_LIBRARIES} ${PYTHON_LIBRARIES} ${CPP_PLATFORM_LIBS})
install(TARGETS octopython DESTINATION ${LIBRARY_INSTALL_DIR})
install(TARGETS octopython DESTINATION ${PYTHON_INSTALL_DIR})

install(FILES src/version_info/__init__.py DESTINATION ${PYTHON_INSTALL_DIR}/version_info)
file(GLOB timbafiles "${CMAKE_CURRENT_SOURCE_DIR}/src/*.py")
install(FILES ${timbafiles} DESTINATION ${PYTHON_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(octopython ${PYTHON_LIBRARIES})
