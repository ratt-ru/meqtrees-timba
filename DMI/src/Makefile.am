# BUILT_SOURCES = AID-Global-Registry.cc
GLOBREG = AID-Global-Registry.cc

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
DataList.h			\
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
$(GLOBREG) \
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
DataList.cc			\
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

glishdir = $(libexecdir)/glish
dist_glish_SCRIPTS = dmitypes.g

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common

# rule for generating the global AID registry
MAKEGLOBREG	= $(srcdir)/makeglobreg.pl

$(srcdir)/$(GLOBREG): $(AID_MAP_GLOBAL) $(MAKEGLOBREG)
	$(MAKEGLOBREG) $< $@


