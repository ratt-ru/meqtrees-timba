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
MEQPACKAGE_ADD_LIBRARIES(apputils)
