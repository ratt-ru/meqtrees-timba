CXXFLAGS += -Wno-unknown-pragmas

INCLUDES += -I$(lofar_sharedir)/../CEP/CPA/PSCF/src

lib_LTLIBRARIES = libdmi.la

libdmi_la_SOURCES =   Debug.cc    DMI.cc \
  AtomicID.cc         CountedRefTarget.cc    HIID.cc               TypeInfo.cc   \
  BlockSet.cc         DataField.cc           HIIDSet.cc   \
  BlockableObject.cc  DataRecord.cc          NestableContainer.cc   \
  CountedRefBase.cc   DynamicTypeManager.cc  SmartBlock.cc \
  AID-DMI-Registry.cc
  
# script used to generate AID maps
MAPBUILDER = $(top_srcdir)/src/build_aid_maps.pl 

# this is for the DMI directory only 
ITERBUILDER = $(top_srcdir)/src/build_type_iter.pl 

# All .aidlist files below this dir will be scanned
BASELISTDIR = $(lofar_sharedir)/..

# Your package's subdirectory
AID_DIR = $(top_srcdir)/src

aidlists := $(shell find $(BASELISTDIR) -name \*.aidlist)

aids: 
	$(MAPBUILDER) $(aidlists) $(AID_DIR)/*.h 
	$(ITERBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(top_srcdir)/src/TypeIterMacros.h
  
all_aids: 
	$(MAPBUILDER) $(aidlists)  `find $(BASELISTDIR) -name \*.h` 
	$(ITERBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(top_srcdir)/src/TypeIterMacros.h 
  
clean_aids: 
	rm -f $(aidlists)
	@echo "Removed all aidlist files"
  

include $(lofar_sharedir)/Makefile.common

