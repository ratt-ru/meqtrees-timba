# BUILT_SOURCES = AID-Global-Registry.cc
GLOBREG = AID-Global-Registry.cc

DOCHDRS		 	=	\
AtomicID.h			\
BlockSet.h			\
BObj.h		\
BOIO.h \
ConfigMgr.h \
CountedRef.h			\
CountedRefBase.h		\
CountedRefTarget.h		\
DMI.h				\
NumArray.h			\
Vec.h			\
List.h			\
Record.h			\
DynamicTypeManager.h		\
HIID.h				\
Container.h		\
ContainerIter.h \
Packer.h			\
Registry.h			\
SmartBlock.h			\
Timestamp.h \
TypeId.h			\
TypeInfo.h

lib_LTLIBRARIES = libdmi.la

libdmi_la_SOURCES = $(DOCHDRS)	\
AID-DMI-Registry.cc		\
$(GLOBREG) \
DMI.cc				\
Registry.cc \
AtomicID.cc			\
TypeInfo.cc			\
SmartBlock.cc			\
HIID.cc				\
BlockSet.cc			\
CountedRefBase.cc		\
CountedRefTarget.cc		\
BObj.cc		\
DynamicTypeManager.cc		\
Container.cc		\
Vec.cc			\
NumArray.cc			\
List.cc			\
Record.cc			\
BOIO.cc \
Timestamp.cc \
ConfigMgr.cc \
AID-DMI.h			\
TID-DMI.h			\
TypeIterMacros.h

CXXFLAGS += -D_GNU_SOURCE 

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

# rule for generating the global AID registry
MAKEGLOBREG	= $(srcdir)/makeglobreg.pl

$(srcdir)/$(GLOBREG): $(AID_MAP_GLOBAL) $(MAKEGLOBREG)
	$(MAKEGLOBREG) $< $@



AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
