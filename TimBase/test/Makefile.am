check_PROGRAMS	      =	tDebug tStringUtil \
			tLorrays testSocket \
			tTimer

# programs to run through supplied checktools
CHECKTOOLPROGS 	      =	tDebug tStringUtil \
			tLorrays tTimer
#ENDCHECKTOOLPROGS

TESTS	= tDebug_test.sh \
	  tStringUtil_test.sh \
	  tLorrays_test.sh    \
	  tTimer

tDebug_SOURCES			= tDebug.cc
tDebug_LDADD			= ../src/libtimbase.la
tDebug_DEPENDENCIES		= ../src/libtimbase.la $(LOFAR_DEPEND)

testSocket_SOURCES		= testSocket.cc
testSocket_LDADD		= ../src/libtimbase.la	
testSocket_DEPENDENCIES		= ../src/libtimbase.la $(LOFAR_DEPEND)

tStringUtil_SOURCES		= tStringUtil.cc
tStringUtil_LDADD		= ../src/libtimbase.la	
tStringUtil_DEPENDENCIES	= ../src/libtimbase.la $(LOFAR_DEPEND)

tLorrays_SOURCES		= tLorrays.cc
tLorrays_LDADD			= ../src/libtimbase.la	
tLorrays_DEPENDENCIES		= ../src/libtimbase.la $(LOFAR_DEPEND)

tTimer_SOURCES			= tTimer.cc
tTimer_LDADD			= ../src/libtimbase.la	
tTimer_DEPENDENCIES		= ../src/libtimbase.la $(LOFAR_DEPEND)

TESTS_ENVIRONMENT		= lofar_sharedir=$(lofar_sharedir)


include $(top_srcdir)/Makefile.common
