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

XFAIL_TESTS		= tLorrays_test.sh

tDebug_SOURCES			= tDebug.cc
tDebug_LDADD			= ../src/libcommon.la
tDebug_DEPENDENCIES		= ../src/libcommon.la $(LOFAR_DEPEND)

testSocket_SOURCES		= testSocket.cc
testSocket_LDADD		= ../src/libcommon.la	
testSocket_DEPENDENCIES		= ../src/libcommon.la $(LOFAR_DEPEND)

tStringUtil_SOURCES		= tStringUtil.cc
tStringUtil_LDADD		= ../src/libcommon.la	
tStringUtil_DEPENDENCIES	= ../src/libcommon.la $(LOFAR_DEPEND)

tLorrays_SOURCES		= tLorrays.cc
tLorrays_LDADD			= ../src/libcommon.la	
tLorrays_DEPENDENCIES		= ../src/libcommon.la $(LOFAR_DEPEND)

tTimer_SOURCES			= tTimer.cc
tTimer_LDADD			= ../src/libcommon.la	
tTimer_DEPENDENCIES		= ../src/libcommon.la $(LOFAR_DEPEND)

TESTS_ENVIRONMENT		= lofar_sharedir=$(lofar_sharedir)


include $(lofar_sharedir)/Makefile.common
