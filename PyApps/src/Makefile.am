CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE -I/usr/include/python2.3

lib_LTLIBRARIES = py_app_launcher.la

DOCHDRS = 

py_app_launcher_la_SOURCES = \
  py_app_launcher.cc
  
py_app_launcher_la_LDFLAGS = -module

py_app_launcher_la_LIBADD = 
#$(lofar_sharedir)/../CEP/CPA/AppAgent/AppAgent/build/gnu3_debug/src/libappagent.la \
#  -llog4cplus 

py_app_launcher_la_DEPENDENCIES = $(LOFAR_DEPEND)

bin_PROGRAMS        =

check_PROGRAMS   		= 

pythondir = $(libexecdir)/python

timbadir = $(pythondir)/Timba

appdir = $(pythondir)/Timba/Apps
griddir = $(pythondir)/Timba/Grid
guidir = $(pythondir)/Timba/GUI
meqdir = $(pythondir)/Timba/Meq
plugindir = $(pythondir)/Timba/Plugins
glishdir = $(libexecdir)/glish/plugins
dist_bin_SCRIPTS = meqbrowser.py 

dist_python_SCRIPTS = 

dist_timba_SCRIPTS = pretty_print.py  

dist_app_SCRIPTS = Apps/__init__.py \
  Apps/app_defaults.py Apps/app_proxy.py Apps/meqserver.py

dist_gui_SCRIPTS = GUI/__init__.py \
  GUI/app_proxy_gui.py  GUI/meqserver_gui.py  \
  GUI/pixmaps.py        GUI/browsers.py       \
  GUI/treebrowser.py 
  
dist_meq_SCRIPTS = Meq/__init__.py \
  Meq/meq.py Meq/meqds.py 
  
dist_plugin_SCRIPTS = \
  Plugins/ComplexColorMap.py   Plugins/__init__.py             Plugins/plot_printer.py     \
  Plugins/ComplexDisplay.py    Plugins/array_plotter.py        Plugins/pyfits.py          \
  Plugins/ComplexScaleDraw.py  Plugins/display_image.py        Plugins/realvsimag.py      \
  Plugins/ErrorBar.py          Plugins/hippo_array_plotter.py  Plugins/result_plotter.py \
  Plugins/parm_plotter.py    Plugins/UVPAxis.py            Plugins/node_execute.py     \
  Plugins/parmfiddler.py
  
dist_grid_SCRIPTS = Grid/__init__.py \
  Grid/Services.py Grid/Workspace.py Grid/Page.py \
  Grid/CellBlock.py Grid/Cell.py Grid/Debug.py

dist_glish_SCRIPTS = Plugins/MSinfo.g

include $(lofar_sharedir)/Makefile.aids
include $(lofar_sharedir)/Makefile.common
