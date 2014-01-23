MEQPACKAGE(AppUtils AppAgent)
set(appUtils_includes
    src/AID-AppUtils.h
    src/MSChannelDebugContext.h
    src/MSChannelVocabulary.h
    src/MSInputChannel.h
    src/MSOutputChannel.h
    src/MSSeqOutputChannel.h
    src/TID-AppUtils.h
    src/TypeIter-AppUtils.h
)
INCLUDE_SETUP(AppUtils ${appUtils_includes})
set(appUtils_src
    src/addbitflagcol.cc
    src/AID-AppUtils-Registry.cc
    src/MSChannelDebugContext.cc
    src/MSInputChannel.cc
    src/MSOutputChannel.cc
    src/MSSeqOutputChannel.cc
    )
add_library(apputils ${appUtils_src})
install(TARGETS apputils DESTINATION ${LIBRARY_INSTALL_DIR})
target_link_libraries(apputils casa_ms)
MEQPACKAGE_ADD_LIBRARIES(apputils)

add_executable(addbitflagcol src/addbitflagcol.cc)
target_link_libraries(addbitflagcol ${MEQPACKAGE_LIBRARIES} ${CPP_PLATFORM_LIBS})
INSTALL(TARGETS addbitflagcol RUNTIME DESTINATION bin)

add_executable(addtiledmscol src/addtiledmscol.cc)
target_link_libraries(addtiledmscol ${MEQPACKAGE_LIBRARIES} ${CPP_PLATFORM_LIBS})
INSTALL(TARGETS addtiledmscol RUNTIME DESTINATION bin)

add_executable(wsrt_j2convert src/wsrt_j2convert.cc)
target_link_libraries(wsrt_j2convert ${MEQPACKAGE_LIBRARIES} ${CPP_PLATFORM_LIBS})
INSTALL(TARGETS wsrt_j2convert RUNTIME DESTINATION bin)

