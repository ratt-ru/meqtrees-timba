CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

lib_LTLIBRARIES = py_app_launcher.la

DOCHDRS = 

py_app_launcher_la_SOURCES = \
  py_app_launcher.cc
  
py_app_launcher_la_LDFLAGS = -module

py_app_launcher_la_LIBADD = $(lofar_sharedir)/../CEP/CPA/AppAgent/AppAgent/build/gnu3_debug/src/libappagent.la \
  -llog4cplus 

py_app_launcher_la_DEPENDENCIES = $(LOFAR_DEPEND)

check_PROGRAMS   		= 

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common
