
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

EXTRA_DIST = build_aid_maps.pl build_type_iter.pl atomicid.list

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
#	$(ITERBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(top_srcdir)/src/TypeIterMacros.h

all_aids: 
	$(MAPBUILDER) $(aidlists)  `find $(BASELISTDIR) -name \*.h` 
#	$(ITERBUILDER) `find $(BASELISTDIR) -name \*.aidlist` $(top_srcdir)/src/TypeIterMacros.h 

clean_aids: 
	rm -f $(aidlists)
	@echo "Removed all aidlist files"


include $(lofar_sharedir)/Makefile.common

