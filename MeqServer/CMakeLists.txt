MEQPACKAGE(MeqServer AppUtils MeqMPI MEQ MeqNodes VisCube OCTOPUSSY OCTOPython DMI TimBase)
set(meqServer_includes
    src/AID-MeqServer.h
    src/MeqPython.h
    src/MeqServer.h
    src/MeqUtils.h
    #src/PyFunctionNode.h
    src/PyNode.h
    src/PyTensorFuncNode.h
    src/Sink.h
    src/Spigot.h
    src/TID-MeqServer.h
    src/TypeIter-MeqServer.h
    src/VisDataMux.h
    src/VisHandlerNode.h
    src/py3compat.h
)
INCLUDE_SETUP(MeqServer ${meqServer_includes})

# ---- library 
set(meqServer_lib_src
    src/AID-MeqServer-Registry.cc
    src/MeqPython.cc
    src/MeqServer.cc
    src/mequtils.cc
    src/octolistener.cc
    #src/PyFunctionNode.cc
    src/PyNode.cc
    src/PyTensorFuncNode.cc
    src/Sink.cc
    src/Spigot.cc
    src/VisDataMux.cc
    src/VisHandlerNode.cc
    )
add_library(meqserver-lib ${meqServer_lib_src})
install(TARGETS meqserver-lib DESTINATION ${LIBRARY_INSTALL_DIR})
FILE(GLOB timbafiles "${CMAKE_CURRENT_SOURCE_DIR}/src/*.py")
install(FILES ${timbafiles} DESTINATION ${PYTHON_INSTALL_DIR})
SET_TARGET_PROPERTIES(meqserver-lib PROPERTIES OUTPUT_NAME "meqserver")
MEQPACKAGE_ADD_LIBRARIES(meqserver-lib)


# -- executables
if (CUDA_FOUND)
  cuda_add_executable(meqserver src/meqserver_main.cc ${CUDA_SRC})
else(CUDA_FOUND)
  add_executable(meqserver src/meqserver_main.cc)
endif(CUDA_FOUND)
#message( libs=${MEQPACKAGE_LIBRARIES} )
IF(APPLE)
    # Link the CoreFoundation framework so that it is initialised in the main thread of meqserver
    # on loading up. Otherwise it may inadvertently be pulled in when constructing a meqnode
    # (e.g. via a Qt import), which crashes meqserver with a SIGTRAP (signal 5) as CFInitialize
    # wants to be run in the main thread only (since OS X 10.6).
    include_directories(/System/Library/Frameworks)
    find_library(CF_LIBRARY CoreFoundation)
    target_link_libraries(meqserver ${MEQPACKAGE_LIBRARIES} ${CPP_PLATFORM_LIBS} ${CF_LIBRARY})
ELSE(APPLE)
    target_link_libraries(meqserver ${MEQPACKAGE_LIBRARIES} ${CPP_PLATFORM_LIBS})
ENDIF(APPLE)
INSTALL(TARGETS meqserver RUNTIME DESTINATION bin)
