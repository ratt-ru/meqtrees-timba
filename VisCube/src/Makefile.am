dmi_dir = $(lofar_sharedir)/../DMI

CXXFLAGS += -Wno-unused

lib_LTLIBRARIES = libviscube.la

libviscube_la_SOURCES = \
  AID-VisCube-Registry.cc \
  VisCommon.cc \
  TableFormat.cc \
  ColumnarTableTile.cc \
  VisTile.cc \
  VisCube.cc \
  VisCubeSet.cc
  
# script used to generate AID maps
MAPBUILDER = $(dmi_dir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/src

aids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h 
 

include $(lofar_sharedir)/Makefile.common

