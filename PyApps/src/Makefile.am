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

pythondir = $(libexecdir)/python
dist_python_SCRIPTS = \
  app_defaults.py  app_proxy_gui.py  meqbrowser.py  meqserver_gui.py  \
  pretty_print.py  app_pixmaps.py    app_proxy.py   gridded_workspace.py \
  meq.py         meqserver.py


include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common
