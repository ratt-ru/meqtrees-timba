CXXFLAGS += -D_GNU_SOURCE 

lib_LTLIBRARIES = liboctopussy.la

DOCHDRS =  LatencyVector.h  Octopussy.h \
  AppManagerWP.h     LoggerWP.h               ReflectorWP.h \
  AppRegistry.h      Message.h                Subscriptions.h \
  ConnectionMgrWP.h  MsgAddress.h             \
  Dispatcher.h       MTGatewayWP.h            \
  Gateways.h         Octoproxy.h              WorkProcess.h \
  GatewayWP.h        OctoproxyWP.h            WPInterface.h \
  GWClientWP.h       OctopussyConfig.h \
  GWServerWP.h       OctopussyDebugContext.h

liboctopussy_la_SOURCES = Dispatcher.cc Octopussy.cc Message.cc  MsgAddress.cc \
	WPInterface.cc WorkProcess.cc OctopussyDebugContext.cc \
  GWClientWP.cc GWServerWP.cc GatewayWP.cc MTGatewayWP.cc MTGatewayWP2.cc \
  LoggerWP.cc LatencyVector.cc OctopussyConfig.cc \
  Subscriptions.cc ReflectorWP.cc AppRegistry.cc \
  Octoproxy.cc OctoproxyWP.cc \
  AID-OCTOPUSSY-Registry.cc
  
#  AppManagerWP.cc 
  

include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
