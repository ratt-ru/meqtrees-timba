# BUILT_SOURCES = Global-Registry.cc

DOCHDRS		 	=	\
AtomicID.h			\
BlockSet.h			\
BlockableObject.h		\
BOIO.h \
Common.h			\
ConfigMgr.h \
CountedRef.h			\
CountedRefBase.h		\
CountedRefTarget.h		\
DMI.h				\
DataArray.h			\
DataField.h			\
DataRecord.h			\
DynamicTypeManager.h		\
HIID.h				\
HIIDSet.h			\
NestableContainer.h		\
NCIter.h \
Packer.h			\
Registry.h			\
SmartBlock.h			\
Timestamp.h \
TypeId.h			\
TypeInfo.h

lib_LTLIBRARIES = libdmi.la

libdmi_la_SOURCES = $(DOCHDRS)	\
AID-DMI-Registry.cc		\
Global-Registry.cc \
AtomicID.cc			\
BlockSet.cc			\
BlockableObject.cc		\
BOIO.cc \
ConfigMgr.cc \
CountedRefBase.cc		\
CountedRefTarget.cc		\
DMI.cc				\
DataArray.cc			\
DataField.cc			\
DataRecord.cc			\
DynamicTypeManager.cc		\
HIID.cc				\
HIIDSet.cc			\
NestableContainer.cc		\
NCIter.cc \
SmartBlock.cc			\
Timestamp.cc \
TypeInfo.cc			\
AID-DMI.h			\
DataAcc-Const.h			\
DataAcc-NonConst.h		\
TID-DMI.h			\
TypeIterMacros.h

CXXFLAGS += -D_GNU_SOURCE 
# CXXFLAGS += -D_GNU_SOURCE -DUSE_THREADS -pthread

# EXTRA_DIST = build_aid_maps.pl build_type_iter.pl atomicid.list

# rules for generating the global AID registry
# this is a list of all the packages that contain any registries
REGISTRY_PACKAGES = \
  DMI    \
  CEP/CPA/OCTOPUSSY   \
  CEP/CPA/OCTOGlish   \
  CEP/CPA/VisCube   \
  CEP/CPA/AppAgent/VisAgent   \
  CEP/CPA/AppAgent/AppAgent   \
  CEP/CPA/AppAgent/OctoAgent   \
  CEP/CPA/AppAgent/MSVisAgent   \
  CEP/CPA/AppAgent/Solver   \
  CEP/CPA/AppAgent/AppUtils   \
  CEP/CPA/uvplot   

REGISTRY_FILES = $(foreach pkg,$(REGISTRY_PACKAGES),$(wildcard $(lofar_sharedir)/../$(pkg)/src/AID-*-Registry.cc))

$(top_srcdir)/src/Global-Registry.cc: $(top_srcdir)/src/Global-Registry.header $(REGISTRY_FILES)
	cp $< $@
	(for f in $(REGISTRY_FILES); do grep "AtomicID::registerId" $$f; done)|sort|uniq >>$@
	cat $(top_srcdir)/src/Global-Registry.footer >>$@

# clean_aids: 
#	rm -f $(aidlists)
#	@echo "Removed all aidlist files"

globreg: Global-Registry.cc

.PHONY: globreg 

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

