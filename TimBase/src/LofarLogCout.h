//  LofarLogCout.h: Macro interface to the cout/cerr logging implementation
//
//  Copyright (C) 2004
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

//# No include guard is used, because it should only be included indirectly
//# by LofarLogger.h (and by LofarLogCout.cc).

#include <Common/lofar_iostream.h>
#include <Common/lofar_sstream.h>
#include <Common/lofar_iomanip.h>
#include <Common/lofar_string.h>
#include <Common/lofar_map.h>
#include <Common/Exception.h>
#ifdef ENABLE_LATENCY_STATS
#include <sys/time.h>
#endif

//# -------------------- Initialisation of the logger module -------------------
//#
// Initializes debug levels the file filename.debug
//	- INIT_LOGGER
//	- INIT_LOGGER_AND_WATCH
//
#define INIT_LOGGER(filename) \
	LOFAR::LFDebug::initLevels (string(filename) + ".debug"); 

//# Note: 'watch' functionality not available
#define INIT_LOGGER_AND_WATCH(filename,interval) \
	INIT_LOGGER(filename)

//# -------------------- Log Levels for the Operator messages -----------------
//#
//# LOG_FATAL_(STR) (message|stream)
//# LOG_ERROR_(STR) (message|stream)
//# LOG_WARN_(STR)  (message|stream)
//# LOG_INFO_(STR)  (message|stream)
//#
#define LOG_FATAL(message)			cLog(1, "FATAL", message)
#define LOG_FATAL_STR(stream) 		cLogstr(1, "FATAL", stream)

#define LOG_ERROR(message) 			cLog(2, "ERROR", message)
#define LOG_ERROR_STR(stream) 		cLogstr(2, "ERROR", stream)

#define LOG_WARN(message) 			cLog(3, "WARN", message)
#define LOG_WARN_STR(stream)		cLogstr(3, "WARN", stream)

#define LOG_INFO(message) 			cLog(4, "INFO", message)
#define LOG_INFO_STR(stream) 		cLogstr(4, "INFO", stream)

//# -------------------- Log Levels for the Integrator -----------------
//#
//# LOG_DEBUG_(STR) (message|stream)
//#
#ifdef DISABLE_DEBUG_OUTPUT
#define LOG_DEBUG(message)
#define LOG_DEBUG_STR(stream)
#else
#define LOG_DEBUG(message) 			cDebug(5, "DEBUG", message)
#define LOG_DEBUG_STR(stream) 		cDebugstr(5, "DEBUG", stream)
#endif	// DISABLE_DEBUG_OUTPUT

//# -------------------- Trace Levels for the Programmer -----------------
//#
//#	ALLOC_TRACER_CONTEXT
//#	INIT_TRACER_CONTEXT		(scope, contextname)
//# ALLOC_TRACER_ALIAS		(parent)
//# LOG_DEBUG_<type>(STR) 	(message|stream)
//#
#ifdef ENABLE_TRACER
#define ALLOC_TRACER_CONTEXT  \
public:	\
  static LFDebug::Context DebugContext; \
  static inline LFDebug::Context & getLFDebugContext() \
            { return DebugContext; }

#define INIT_TRACER_CONTEXT(scope, contextname)  \
  LFDebug::Context scope::DebugContext(contextname)

#define ALLOC_TRACER_ALIAS(other)  \
  static inline LFDebug::Context & getLFDebugContext() \
  { return other::getLFDebugContext(); }

#define LOG_TRACE_LOOP(message)		cTrace(TRACE_LEVEL_LOOP, message)
#define LOG_TRACE_VAR(message)		cTrace(TRACE_LEVEL_VAR, message)
#define LOG_TRACE_CALC(message)		cTrace(TRACE_LEVEL_CALC, message)
#define LOG_TRACE_COND(message)		cTrace(TRACE_LEVEL_COND, message)
#define LOG_TRACE_STAT(message)		cTrace(TRACE_LEVEL_STAT, message)
#define LOG_TRACE_OBJ(message)		cTrace(TRACE_LEVEL_OBJ, message)
#define LOG_TRACE_RTTI(message)		cTrace(TRACE_LEVEL_RTTI, message)
#define LOG_TRACE_FLOW(message)		cTrace(TRACE_LEVEL_FLOW, message)
#define LOG_TRACE_LOOP_STR(stream)	cTracestr(TRACE_LEVEL_LOOP, stream)
#define LOG_TRACE_VAR_STR(stream)	cTracestr(TRACE_LEVEL_VAR, stream)
#define LOG_TRACE_CALC_STR(stream)	cTracestr(TRACE_LEVEL_CALC, stream)
#define LOG_TRACE_COND_STR(stream)	cTracestr(TRACE_LEVEL_COND, stream)
#define LOG_TRACE_STAT_STR(stream)	cTracestr(TRACE_LEVEL_STAT, stream)
#define LOG_TRACE_OBJ_STR(stream)	cTracestr(TRACE_LEVEL_OBJ, stream)
#define LOG_TRACE_RTTI_STR(stream)	cTracestr(TRACE_LEVEL_RTTI, stream)
#define LOG_TRACE_FLOW_STR(stream)	cTracestr(TRACE_LEVEL_FLOW, stream)
#define TRACE_LEVEL_LOOP			18
#define TRACE_LEVEL_VAR				17
#define TRACE_LEVEL_CALC			16
#define TRACE_LEVEL_COND			15
#define TRACE_LEVEL_STAT			14
#define TRACE_LEVEL_OBJ				13
#define TRACE_LEVEL_RTTI			12
#define TRACE_LEVEL_FLOW			11

//# The numbering of trace levels in log4cplus is reversed compared to Debug.
//# This macro converts the Debug trace level to the log4cplus trace level.
#define LOG4CPLUS_LEVEL(level) TRACE_LEVEL_LOOP-level+1

//#
//# LOG_TRACE_LIFETIME(_STR) (level, message|stream)
//#
#define LOG_TRACE_LIFETIME_STR(level, stream) \
	LFDebug::Tracer objname; \
    if( LFDebugCheck(level) ) { \
		constructStream(stream) \
		objname.startMsg (LOG4CPLUS_LEVEL(level), __FILE__, __LINE__, \
                        __PRETTY_FUNCTION__, oss.str().c_str(), 0); \
    }
#define LOG_TRACE_LIFETIME(level,message) \
	LOG_TRACE_LIFETIME_STR(level, message)

//# ---------- implementation details tracer part ----------
#define cTrace(level, message)		cDebug(level, "TRACE" << LOG4CPLUS_LEVEL(level) << " TRC." << getLFDebugContext().name(), message)
#define cTracestr(level,stream) 	cDebugstr(level, "TRACE" << LOG4CPLUS_LEVEL(level) << " TRC." << getLFDebugContext().name(), stream)

#else	// ENABLE_TRACER
//# define dummies if tracing is disabled
#define ALLOC_TRACER_CONTEXT 
#define INIT_TRACE_CONTEXT(scope, contextname) 
#define ALLOC_TRACER_ALIAS(other) 

#define LOG_TRACE_LOOP(message)
#define LOG_TRACE_VAR(message)
#define LOG_TRACE_CALC(message)	
#define LOG_TRACE_COND(message)	
#define LOG_TRACE_STAT(message)	
#define LOG_TRACE_OBJ(message)
#define LOG_TRACE_RTTI(message)
#define LOG_TRACE_FLOW(message)
#define LOG_TRACE_LOOP_STR(stream)
#define LOG_TRACE_VAR_STR(stream)
#define LOG_TRACE_CALC_STR(stream)
#define LOG_TRACE_COND_STR(stream)
#define LOG_TRACE_STAT_STR(stream)
#define LOG_TRACE_OBJ_STR(stream)
#define LOG_TRACE_RTTI_STR(stream)
#define LOG_TRACE_FLOW_STR(stream)
#define TRACE_LEVEL_LOOP			0
#define TRACE_LEVEL_VAR				0
#define TRACE_LEVEL_CALC			0
#define TRACE_LEVEL_COND			0
#define TRACE_LEVEL_STAT			0
#define TRACE_LEVEL_OBJ				0
#define TRACE_LEVEL_RTTI			0
#define TRACE_LEVEL_FLOW			0

#define LOG_TRACE_LIFETIME_STR(level, stream)
#define LOG_TRACE_LIFETIME(level,message)

#endif	// ENABLE_TRACER

//# -------------------- Assert and FailWhen --------------------
//#
//# THROW			(exception,stream)
//# (DBG)ASSERT		(condition,stream)
//# (DBG)FAILWHEN	(condition,stream)
//#
//# Note: only THROW needs to be defines here, the others are buiold on THROW
//# in the LofarLogger.h file.

#undef THROW
// possible object debug status. 
#define THROW(exc,msg)  { \
	constructStream(msg) \
	cLog(1, "EXCEPTION", oss.str()); \
	throw(exc(oss.str(), __HERE__)); \
	}

//# ---------- implementation details generic part ----------

#define LFDebugCheck(level)	getLFDebugContext().check(level)

#define DebugTestAndLog(level) \
	if (LFDebugCheck(level) && LOFAR::LFDebug::stream_time()) \
		LOFAR::LFDebug::getDebugStream()

#define	constructStream(stream) \
	std::ostringstream	oss; \
	oss << stream;

#define	cLog(level,levelname,message) \
	DebugTestAndLog(level) << setw(5) << left << levelname \
		<< " [" << LOFARLOGGER_FULLPACKAGE << "] " << message << endl;

#define cLogstr(level,levelname,stream) { \
		constructStream(stream) \
		cLog(level,levelname,oss.str().c_str()) \
	}

#define	cDebug(level,levelname,message) \
	DebugTestAndLog(level) << setw(5) << left << levelname \
		<< " [" << LOFARLOGGER_FULLPACKAGE << "] " << message \
		<< ", File:" << __FILE__ << ", Line:" << __LINE__ << endl;

#define cDebugstr(level,levelname,stream)  { \
		constructStream(stream) \
		cDebug(level,levelname,oss.str().c_str()) \
	}


//#-------------------- END OF MACRO DEFINITIONS --------------------#//

namespace LOFAR
{
  namespace LFDebug
  {
    extern ostream * dbg_stream_p;
  
    inline ostream & getDebugStream () { return *dbg_stream_p; }

    // Typedef the exception type, so we can change whenever needed.
    EXCEPTION_CLASS(Fail,LOFAR::Exception);

    // sets level of given context
    bool setLevel (const string &context,int level);
     
    void initLevels (const string& fname);
    // loads debug levels from file.
    void loadLevels (const string& fname);

    // appends strings and inserts a space, if needed
    string& append( string &str,const string &str2,const string &sep = " " );
    // sprintfs to a string object, returns it
    const string ssprintf( const char *format,... );
    // sprintfs to a string, with append & insertion of spaces
    int appendf( string &str,const char *format,... );
  
    class Context 
    {
    public:
      Context (const string &name, Context *parent_ = 0);
      ~Context();
    
      bool check (int level) const;
      int level () const;
      int setLevel (int value);
      const string& name () const;
      static void initialize ();
        
    private:
      static bool initialized;
      int debug_level;
      string context_name;
      Context *parent;
    };

    //## Other Operations (inline)
    inline bool Context::check (int level) const
    {
      if( !initialized )
        return false;
      if( parent && parent->check(level) )
        return true;
      return level <= debug_level;
    }

    inline int Context::level () const
    {
      return debug_level;
    }

    inline int Context::setLevel (int value)
    {
      debug_level = value;
      return value;
    }

    inline const string& Context::name () const
    {
      return context_name;
    }
  
    inline void Context::initialize ()
    {
      initialized = true;
    }

#ifdef ENABLE_TRACER
    class Tracer
    {
    public:
      Tracer() : itsDo(false) {}

      void startMsg (int level,
                     const char* file, int line, const char* func,
                     const char* msg, const void* objPtr);

      ~Tracer()
      { if (itsDo) endMsg(); }

    private:
      Tracer(const Tracer&);
      Tracer& operator= (const Tracer&);
      void endMsg();

      bool    itsDo;
      int     itsLevel;
      string  itsMsg;
    };
#endif

#ifdef ENABLE_LATENCY_STATS
    extern struct timeval tv_init;
    inline int printf_time ()
    { 
      struct timeval tv; gettimeofday(&tv,0);
      printf("%ld.%06ld ",tv.tv_sec-tv_init.tv_sec,tv.tv_usec);
      return 1;
    }
    inline int stream_time ()
    {
      struct timeval tv; gettimeofday(&tv,0);
      getDebugStream() << formatString("%ld.%06ld ",tv.tv_sec-tv_init.tv_sec,tv.tv_usec);
      return 1;
    }
#else
    inline int printf_time () { return 1; };
    inline int stream_time () { return 1; };
#endif

    extern Context DebugContext;
    inline Context & getLFDebugContext ()  { return DebugContext; }

  } // namespace LFDebug


  // Default DebugContext is the one in LFDebug.
  using LFDebug::getLFDebugContext;

} // namespace LOFAR
