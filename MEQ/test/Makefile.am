check_PROGRAMS 		= tForest tVellsSlicer

TESTS			= tForest tVellsSlicer

tForest_SOURCES 	= tForest.cc 
tForest_LDADD		= ../src/libmeq.la 
tForest_DEPENDENCIES	= ../src/libmeq.la $(LOFAR_DEPEND)

tVellsSlicer_SOURCES 	= tVellsSlicer.cc 
tVellsSlicer_LDADD	= ../src/libmeq.la 
tVellsSlicer_DEPENDENCIES = ../src/libmeq.la $(LOFAR_DEPEND)

TESTS_ENVIRONMENT		= lofar_sharedir=$(lofar_sharedir)

include $(top_srcdir)/Makefile.common

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
