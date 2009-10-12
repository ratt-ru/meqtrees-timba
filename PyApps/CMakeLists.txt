MEQPACKAGE(PyApps MEQ OCTOPython OCTOPUSSY DMI)

set(mequtils_src
    src/mequtils_symlink.cc
    )
add_library(mequtils SHARED ${mequtils_src})
set_target_properties(mequtils PROPERTIES PREFIX "")
target_link_libraries(mequtils ${MEQPACKAGE_LIBRARIES} ${PYTHON_LIBRARIES} ${CPP_PLATFORM_LIBS})
install(TARGETS mequtils DESTINATION ${PYTHON_INSTALL_DIR})

set(parmtables_src
    src/parmtables.cc
    )
add_library(parmtables SHARED ${parmtables_src})
set_target_properties(parmtables PROPERTIES PREFIX "")
target_link_libraries(parmtables ${MEQPACKAGE_LIBRARIES} ${PYTHON_LIBRARIES} ${CPP_PLATFORM_LIBS})
install(TARGETS parmtables DESTINATION ${PYTHON_INSTALL_DIR})

MEQPACKAGE_ADD_LIBRARIES(mequtils parmtables)

# python installation targets
install(PROGRAMS src/meqbrowser.py src/tdlrun.py src/trut.py src/trutify DESTINATION bin)
install(FILES src/pretty_print.py DESTINATION ${PYTHON_INSTALL_DIR})
install(DIRECTORY src/Apps DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE )
install(DIRECTORY src/Contrib DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE )
install(DIRECTORY src/Grid DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE)
install(DIRECTORY src/GUI DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE)
install(DIRECTORY src/Plugins DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE)
install(DIRECTORY src/Trut DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE)
install(DIRECTORY src/TDL DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE)
install(DIRECTORY src/Meq DESTINATION ${PYTHON_INSTALL_DIR} FILES_MATCHING PATTERN "*.py" PATTERN ".svn" EXCLUDE)

# icon installation
#FILE(GLOB icons "${CMAKE_CURRENT_SOURCE_DIR}/src/icons")
install(DIRECTORY src/icons/ 
        DESTINATION ${ICON_INSTALL_DIR}
        PATTERN ".svn" EXCLUDE
    )
