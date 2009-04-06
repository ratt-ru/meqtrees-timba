MEQPACKAGE(PyApps MEQ OCTOPython OCTOPUSSY DMI)

set(mequtils_src
    src/mequtils_symlink.cc
    )
add_library(mequtils ${mequtils_src})
install(TARGETS mequtils DESTINATION ${LIBRARY_INSTALL_DIR})

set(parmtables_src
    src/parmtables.cc
    )
add_library(parmtables ${parmtables_src})
install(TARGETS parmtables DESTINATION ${LIBRARY_INSTALL_DIR})

MEQPACKAGE_ADD_LIBRARIES(mequtils)

# python installation targets
install(PROGRAMS src/meqbrowser.py src/tdlrun.py src/trut.py src/trutify src/Purr/purr.py DESTINATION bin)
install(DIRECTORY src/Apps DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")
install(DIRECTORY src/Grid DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")
install(DIRECTORY src/GUI DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")
install(DIRECTORY src/Purr DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")
install(DIRECTORY src/Plugins DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")
install(DIRECTORY src/Trut DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")
install(DIRECTORY src/Meq DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py")

# icon installation
#FILE(GLOB icons "${CMAKE_CURRENT_SOURCE_DIR}/src/icons")
install(DIRECTORY src/icons/ 
        DESTINATION ${ICON_INSTALL_DIR}
        PATTERN ".svn" EXCLUDE
    )
