check_PROGRAMS 		= tMeqVells tMeqPolc tMeq tSolver

TESTS			= tMeqVells tMeqPolc_test.sh tMeq tSolver

tMeqVells_SOURCES 	= tMeqVells.cc 
tMeqVells_LDADD		= ../src/libmeqnodes.la 
tMeqVells_DEPENDENCIES	= ../src/libmeqnodes.la $(LOFAR_DEPEND)

tMeqPolc_SOURCES 	= tMeqPolc.cc 
tMeqPolc_LDADD		= ../src/libmeqnodes.la 
tMeqPolc_DEPENDENCIES	= ../src/libmeqnodes.la $(LOFAR_DEPEND)

tMeq_SOURCES	 	= tMeq.cc 
tMeq_LDADD		= ../src/libmeqnodes.la 
tMeq_DEPENDENCIES	= ../src/libmeqnodes.la $(LOFAR_DEPEND)

tSolver_SOURCES	 	= tSolver.cc 
tSolver_LDADD		= ../src/libmeqnodes.la 
tSolver_DEPENDENCIES	= ../src/libmeqnodes.la $(LOFAR_DEPEND)

TESTS_ENVIRONMENT		= lofar_sharedir=$(lofar_sharedir)

include $(lofar_sharedir)/Makefile.common

AM_CPPFLAGS = -DMAKE_LOFAR_SYMBOLS_GLOBAL
