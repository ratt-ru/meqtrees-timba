CXXFLAGS += -Wno-unused

lib_LTLIBRARIES = libviscube.la

DOCHDRS = \
  VisVocabulary.h \
  VisCommon.h \
  TableFormat.h \
  ColumnarTableTile.h \
  VisTile.h \
  VisCube.h \
  VisCubeSet.h


libviscube_la_SOURCES = \
  AID-VisCube-Registry.cc \
  VisCommon.cc \
  TableFormat.cc \
  ColumnarTableTile.cc \
  VisTile.cc \
  VisCube.cc \
  VisCubeSet.cc
  
include $(lofar_sharedir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
