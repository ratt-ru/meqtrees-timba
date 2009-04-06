MEQPACKAGE(AppAgent MEQ VisCube OCTOPUSSY OCTOPython DMI TimBase)
set(appAgent_includes
    src/AID-AppAgent.h
    src/BOIOChannel.h
    src/EventChannel.h
    src/EventFlag.h
    src/FileChannel.h
    src/MTQueueChannel.h
    src/OctoChannel.h
    src/OctoEventMux.h
    src/TID-AppAgent.h
    src/TypeIter-AppAgent.h
    src/VisDataVocabulary.h
)
INCLUDE_SETUP(AppAgent ${appAgent_includes})
set(appAgent_src
    src/AID-AppAgent-Registry.cc
    src/BOIOChannel.cc
    src/EventChannel.cc
    src/EventFlag.cc
    src/FileChannel.cc
    src/MTQueueChannel.cc
    src/OctoChannel.cc
    src/OctoEventMux.cc
    )
add_library(appagent ${appAgent_src})
install(TARGETS appagent DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(appagent)
