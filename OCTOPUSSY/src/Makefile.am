dmi_dir = $(lofar_sharedir)/../DMI

CXXFLAGS += -D_GNU_SOURCE 

lib_LTLIBRARIES = liboctopussy.la

liboctopussy_la_SOURCES = Dispatcher.cc  Message.cc  MsgAddress.cc  \
	WPInterface.cc WorkProcess.cc OctopussyDebugContext.cc \
  GWClientWP.cc GWServerWP.cc GatewayWP.cc MTGatewayWP.cc MTGatewayWP2.cc \
  LoggerWP.cc LatencyVector.cc OctopussyConfig.cc \
  Subscriptions.cc ReflectorWP.cc AppRegistry.cc AppManagerWP.cc \
  Octoproxy.cc OctoproxyWP.cc \
  AID-OCTOPUSSY-Registry.cc
  

# script used to generate AID maps
MAPBUILDER = $(dmi_dir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/src


aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h 
 

include $(lofar_sharedir)/Makefile.common

