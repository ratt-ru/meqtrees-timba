
SUBDIRS=. pscf 

CXXFLAGS += -Wno-unknown-pragmas

lib_LTLIBRARIES = libdmi.la

libdmi_la_SOURCES =   Debug.cc    DMI.cc \
  AtomicID.cc         CountedRefTarget.cc    HIID.cc               TypeInfo.cc   \
  BlockSet.cc         DataField.cc           HIIDSet.cc   \
  BlockableObject.cc  DataRecord.cc          NestableContainer.cc   \
  CountedRefBase.cc   DynamicTypeManager.cc  SmartBlock.cc \
  AID-DMI-Registry.cc
  
# script used to generate AID maps
MAPBUILDER = $(top_srcdir)/src/build_aid_maps.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/src

ids:
	$(MAPBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(AID_DIR)/*.h

include $(lofar_sharedir)/Makefile.common

