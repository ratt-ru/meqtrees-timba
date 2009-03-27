INSTHDRS = \
        AipsppMutex.h \
        BlitzToAips.h \
        CheckConfig.h \
        Debug.h \
        Exception.h \
        lofar_algorithm.h \
        lofar_complex.h \
        lofar_deque.h \
        lofar_fstream.h \
        lofar_global_symbol_warning.h \
	      lofar_iomanip.h \
        lofar_iosfwd.h \
        lofar_iostream.h \
        lofar_list.h \
        lofar_map.h \
        lofar_sstream.h \
        lofar_stack.h \
        lofar_string.h \
        lofar_strstream.h \
        LofarTypedefs.h \
        LofarTypes.h \
        lofar_vector.h \
        LofarLogger.h \
        LofarLogCout.h \
        Lonumerics.h \
        Lorrays-Blitz.h \
        Lorrays.h \
        Stopwatch.h \
        StringUtil.h \
        Thread.h \
        TypeNames.h \
        Net/Socket.h \
        Profiling/PerfProfile.h \
        Thread/Condition.h \
        Thread/Key.h \
        Thread/Mutex.h \
        Thread/SmartLock.h \
        Thread/Thread.h \
	Timer.h

NOINSTHDRS =

TCCHDRS = 

nobase_pkginclude_HEADERS = $(INSTHDRS) $(TCCHDRS)

noinst_HEADERS = $(NOINSTHDRS)

DOCHDRS	= $(INSTHDRS) $(NOINSTHDRS)

if USE_NOINST_LIBS
  noinst_LTLIBRARIES       = libtimbase.la
else
  lib_LTLIBRARIES    = libtimbase.la
endif
    
libtimbase_la_SOURCES 	= \
        AipsppMutex.cc \
        Debug.cc \
        Exception.cc \
        Stopwatch.cc \
        StringUtil.cc \
        LofarLogger.cc \
        LofarLogCout.cc \
        Net/Socket.cc \
        Profiling/PerfProfile.cc \
        Thread/SmartLock.cc \
        Thread/Thread.cc \
	Timer.cc
	
libtimbase_la_LIBADD = -lblitz

AM_YFLAGS		= -d -p KeyParse
AM_LFLAGS		= -PKeyTokenize
LEX_OUTPUT_ROOT		= lex.KeyTokenize

# all: gprof-helper.so

gprof-helper.so: $(srcdir)/gprof-helper.c
	$(CC) -shared -fPIC $(srcdir)/gprof-helper.c -o gprof-helper.so -lpthread -ldl


include $(top_srcdir)/Makefile.common
