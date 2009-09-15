INCLUDE_DIRECTORIES(${BLITZ_INCLUDE_DIR})
MEQPACKAGE( TimBase )

set(timbase_includes
    src/AipsppMutex.h
    src/BlitzToAips.h
    src/CheckConfig.h
    src/Debug.h
    src/Exception.h
    src/hexdump.h
    src/lofar_algorithm.h
    src/lofar_complex.h
    src/lofar_deque.h
    src/lofar_fstream.h
    src/lofar_global_symbol_warning.h
    src/lofar_iomanip.h
    src/lofar_iosfwd.h
    src/lofar_iostream.h
    src/lofar_list.h
    src/LofarLogCout.h
    src/LofarLogger.h
    src/lofar_map.h
    src/lofar_sstream.h
    src/lofar_stack.h
    src/lofar_string.h
    src/lofar_strstream.h
    src/LofarTypedefs.h
    src/LofarTypes.h
    src/lofar_vector.h
    src/Lonumerics.h
    src/Lorrays-Blitz.h
    src/Lorrays.h
    src/Stopwatch.h
    src/StringUtil.h
    src/Thread.h
    src/Timer.h
    src/TypeNames.h
)
INCLUDE_SETUP(TimBase ${timbase_includes})
set(timbase_thread_includes
    src/Thread/Condition.h
    src/Thread/Key.h
    src/Thread/Mutex.h
    src/Thread/SmartLock.h
    src/Thread/Thread.h
)
INCLUDE_SETUP(TimBase/Thread ${timbase_thread_includes})
set(timbase_backward_includes
    src/backward/Debug.cc
)
INCLUDE_SETUP(TimBase/backward ${timbase_backward_includes})
set(timbase_net_includes
    src/Net/Socket.h
)
INCLUDE_SETUP(TimBase/Net ${timbase_net_includes})
set(timbase_profiling_includes
    src/Profiling/PerfProfile.h
)
INCLUDE_SETUP(TimBase/Profiling ${timbase_profiling_includes})

set(timbase_src 
    src/AipsppMutex.cc
    src/Debug.cc
    src/Exception.cc
    src/LofarLogCout.cc
    src/LofarLogger.cc
    src/Stopwatch.cc
    src/StringUtil.cc
    src/Timer.cc
    src/Net/Socket.cc
    src/Profiling/PerfProfile.cc
    src/Thread/SmartLock.cc
    src/Thread/Thread.cc
)

add_library(timbase ${timbase_src})
install(TARGETS timbase DESTINATION ${LIBRARY_INSTALL_DIR})
install(PROGRAMS src/gprof-run RENAME meqtrees-gprof-run DESTINATION bin)
MEQPACKAGE_ADD_LIBRARIES(timbase ${BLITZ_LIBRARIES})
