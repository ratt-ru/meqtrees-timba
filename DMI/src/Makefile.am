
SUBDIRS=. pscf

CXXFLAGS += -Wno-unknown-pragmas

lib_LTLIBRARIES = libdmi.la

libdmi_la_SOURCES =   Debug.cc    DMI.cc \
  AtomicID.cc         CountedRefTarget.cc    HIID.cc               TypeInfo.cc   \
  BlockSet.cc         DataField.cc           HIIDSet.cc   \
  BlockableObject.cc  DataRecord.cc          NestableContainer.cc   \
  CountedRefBase.cc   DynamicTypeManager.cc  SmartBlock.cc 

include $(lofar_sharedir)/Makefile.common

