check_PROGRAMS 		= tForest 

TESTS			= tForest 

tForest_SOURCES 	= tForest.cc 
tForest_LDADD		= ../src/libmeq.la 
tForest_DEPENDENCIES	= ../src/libmeq.la $(LOFAR_DEPEND)

TESTS_ENVIRONMENT		= lofar_sharedir=$(lofar_sharedir)

include $(lofar_sharedir)/Makefile.common

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
