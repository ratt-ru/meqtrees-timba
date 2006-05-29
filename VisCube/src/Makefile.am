CXXFLAGS += -Wno-unused

lib_LTLIBRARIES = libviscube.la

DOCHDRS = \
  VisVocabulary.h \
  VisCommon.h \
  TableFormat.h \
  ColumnarTableTile.h \
  VTile.h 
  
#  VCube.h \
#  VCubeSet.h


libviscube_la_SOURCES = \
  AID-VisCube-Registry.cc \
  VisCommon.cc \
  TableFormat.cc \
  ColumnarTableTile.cc \
  VTile.cc 
  
#  VCube.cc \
#  VCubeSet.cc
  
include $(top_srcdir)/Makefile.common
include $(lofar_sharedir)/Makefile.aids


AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
