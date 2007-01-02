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
Exception.h \
NumArray.h			\
NumArrayFuncs.h			\
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

if OLD_LIBTOOL
  lib_LTLIBRARIES = libdmi.la
else
  noinst_LTLIBRARIES = libdmi.la
endif

libdmi_la_SOURCES = $(DOCHDRS)	\
AID-DMI-Registry.cc		\
$(GLOBREG) \
DMI.cc				\
Exception.cc \
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
NumArrayFuncs.cc                \
NumArrayFuncs2.cc               \
NumArrayFuncs3.cc               \
NumArrayFuncs4.cc               \
NumArrayFuncs5.cc               \
NumArrayFuncs6.cc               \
NumArrayFuncs7.cc               \
NumArrayFuncs8.cc               \
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
include $(top_srcdir)/Makefile.common

# rule for generating the global AID registry
MAKEGLOBREG	= $(srcdir)/makeglobreg.pl

$(srcdir)/$(GLOBREG): $(AID_MAP_GLOBAL) $(MAKEGLOBREG)
	$(MAKEGLOBREG) $< $@



AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
