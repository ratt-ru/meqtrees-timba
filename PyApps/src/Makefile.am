CXXFLAGS += -Wall -Wno-unknown-pragmas -Wno-deprecated -D_GNU_SOURCE

lib_LTLIBRARIES = mequtils.la parmtables.la

DOCHDRS = 

mequtils_la_SOURCES = \
  mequtils_symlink.cc
  
mequtils_la_LDFLAGS = -module -lblitz

#mequtils_la_LIBADD = -lblitz

#  ../pkgbldinc/TimBase/.libs/libtimbase.a

mequtils_la_DEPENDENCIES = $(LOFAR_DEPEND)

parmtables_la_SOURCES = parmtables.cc
  
parmtables_la_LDFLAGS = -module -lblitz 
parmtables_la_LIBADD = 

parmtables_la_DEPENDENCIES = $(LOFAR_DEPEND)


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
  GUI/browsers.py       \
  GUI/treebrowser.py 
  
dist_meq_SCRIPTS = Meq/__init__.py \
  Meq/meq.py Meq/meqds.py 
  
dist_plugin_SCRIPTS = \
  Plugins/ComplexColorMap.py   Plugins/__init__.py             Plugins/plot_printer_qt4.py     \
  Plugins/ComplexDisplay.py    Plugins/array_plotter.py        \
  Plugins/ComplexScaleDraw_qt4.py  Plugins/display_image_qt4.py        Plugins/realvsimag_qt4.py      \
  Plugins/ErrorBar_qt4.py          Plugins/hippo_array_plotter.py  Plugins/result_plotter.py \
  Plugins/UVPAxis.py            Plugins/node_execute.py     \
  Plugins/parmfiddler.py     Plugins/guiplot2dnodesettings.py      Plugins/dialog_window_config.py    \
  Plugins/history_plotter.py Plugins/svg_plotter.py
  
dist_grid_SCRIPTS = Grid/__init__.py \
  Grid/Services.py Grid/Workspace.py Grid/Page.py \
  Grid/CellBlock.py Grid/Cell.py Grid/Debug.py

include $(lofar_sharedir)/Makefile.aids
include $(top_srcdir)/Makefile.common
