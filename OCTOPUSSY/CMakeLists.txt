MEQPACKAGE( OCTOPUSSY DMI TimBase )
set(octopussy_includes
    src/AID-OCTOPUSSY.h
    src/ConnectionMgrWP.h
    src/Dispatcher.h
    src/Gateways.h
    src/GatewayWP.h
    src/GWClientWP.h
    src/GWServerWP.h
    src/LatencyVector.h
    src/ListenerWP.h
    src/LoggerWP.h
    src/Message.h
    src/MsgAddress.h
    src/MTGatewayWP.h
    src/Octoproxy.h
    src/OctoproxyWP.h
    src/OctopussyConfig.h
    src/OctopussyDebugContext.h
    src/Octopussy.h
    src/ReflectorWP.h
    src/StatusMonitorWP.h
    src/Subscriptions.h
    src/TID-OCTOPUSSY.h
    src/TypeIter-OCTOPUSSY.h
    src/WorkProcess.h
    src/WPInterface.h
    )
INCLUDE_SETUP(OCTOPUSSY ${octopussy_includes})

set(octopussy_src 
             src/AID-OCTOPUSSY-Registry.cc
             #src/ConnectionMgrWP.cc
             src/Dispatcher.cc
             src/GatewayWP.cc
             src/GWClientWP.cc
             src/GWServerWP.cc
             src/LatencyVector.cc
             src/ListenerWP.cc
             src/LoggerWP.cc
             src/Message.cc
             src/MsgAddress.cc
             src/MTGatewayWP2.cc
             src/MTGatewayWP.cc
             src/octolistener.cc
             src/Octoproxy.cc
             src/OctoproxyWP.cc
             src/Octopussy.cc
             src/OctopussyConfig.cc
             src/OctopussyDebugContext.cc
             src/ReflectorWP.cc
             src/StatusMonitorWP.cc
             src/Subscriptions.cc
             src/WorkProcess.cc
             src/WPInterface.cc
)

add_library(octopussy ${octopussy_src})
install(TARGETS octopussy DESTINATION ${LIBRARY_INSTALL_DIR})
MEQPACKAGE_ADD_LIBRARIES(octopussy)
