CXXFLAGS += -D_GNU_SOURCE 

noinst_LTLIBRARIES = liboctopussy.la

DOCHDRS =  LatencyVector.h  Octopussy.h \
  LoggerWP.h         ReflectorWP.h \
  Message.h          Subscriptions.h \
  MsgAddress.h       Dispatcher.h             MTGatewayWP.h            \
  Gateways.h         Octoproxy.h              WorkProcess.h \
  GatewayWP.h        OctoproxyWP.h            WPInterface.h \
  GWClientWP.h       OctopussyConfig.h        StatusMonitorWP.h \
  GWServerWP.h       OctopussyDebugContext.h ListenerWP.h

liboctopussy_la_SOURCES = Dispatcher.cc Octopussy.cc Message.cc MsgAddress.cc \
  WPInterface.cc WorkProcess.cc OctopussyDebugContext.cc \
  GWClientWP.cc GWServerWP.cc GatewayWP.cc MTGatewayWP.cc MTGatewayWP2.cc \
  LatencyVector.cc OctopussyConfig.cc \
  Subscriptions.cc ReflectorWP.cc \
  Octoproxy.cc OctoproxyWP.cc \
  LoggerWP.cc ListenerWP.cc StatusMonitorWP.cc \
  AID-OCTOPUSSY-Registry.cc
  
  
check_PROGRAMS = octolistener

octolistener_SOURCES 	= octolistener.cc
octolistener_LDADD		= liboctopussy.la
octolistener_DEPENDENCIES	= liboctopussy.la $(LOFAR_DEPEND)
  
  
include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
