CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

lib_LTLIBRARIES = pyparmdb.la

DOCHDRS = 

pyparmdb_la_SOURCES = \
  ParmDBModule.cc
  
pyparmdb_la_LDFLAGS = -module

pyparmdb_la_LIBADD = 	$(prefix)/lib/libparmdb.a \
	$(prefix)/lib/libblob.a \
	$(prefix)/lib/libcommon.a \
	$(AIPSPP)/lib/libtables.a \
	$(AIPSPP)/lib/libcasa.a
pyparmdb_la_DEPENDENCIES = $(LOFAR_DEPEND) \
	$(prefix)/lib/libparmdb.a \
	$(prefix)/lib/libblob.a \
	$(prefix)/lib/libcommon.a 


#$(lofar_sharedir)/../CEP/CPA/AppAgent/AppAgent/build/gnu3_debug/src/libappagent.la \
#  -llog4cplus 


bin_PROGRAMS        =

check_PROGRAMS   		= 

pythondir = $(libexecdir)/python
parmdbdir= $(pythondir)/Timba/ParmDB

dist_parmdb_SCRIPTS = __init__.py \
  ParmDB.py

include $(lofar_sharedir)/Makefile.aids
include $(top_srcdir)/Makefile.common
