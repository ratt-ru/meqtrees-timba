//  Debug.h:
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
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

#ifndef COMMON_DEBUG_H
#define COMMON_DEBUG_H

#ifdef __DEPRECATED
#warning Debug.h is deprecated, please use LofarLogger.h instead. \
To disable this warning use -Wno-deprecated.
#endif

#include <lofar_config.h>
#include <stdlib.h>

#include <TimBase/lofar_iostream.h>
#include <TimBase/lofar_string.h>
#include <TimBase/lofar_fstream.h>
#include <TimBase/lofar_sstream.h>
#include <TimBase/lofar_map.h>
#include <TimBase/Exception.h>
#ifdef ENABLE_LATENCY_STATS
#include <sys/time.h>
#endif



//      =====[ Declaring and implementing debugging contexts ]=====
//      ===========================================================
//
// The system supports multiple debugging contexts. Each context has 
// its own debug message level, which may be initialized from the
// command line and changed at run time. Debug messages (see below)
// are generated only if the level of the message is <= the current
// level of the current debug context.
// 
// A debugging context is identified by a name, and implemented via a 
// Debug::Context object. All debugging macros call the getDebugContext()
// function to determine the current Debug::Context object. Thus, judicious 
// use of namespaces allows these macros to pick the right context depending
// on current program scope.
// 
// You can define a debugging context by placing the appropriate
// magic invocationas in a namespace or a class declaration.
// The following macro, when placed in a header _inside_ your class or
// namespace declarations (.h file), will declare a local debug context:
//
//    LocalDebugContext;
//
// Alternatively, use
//
//    ImportDebugContext(other_class_or_namespace);
//
// to use the same context as that of another class or namespace.
//
// If you declare a local context, your .cc file must define an 
// implementation. To do so, insert this macro:
//
//    InitDebugContext(scope,"contextname");
//
// where "scope" is the class or namespace. This will add the functions 
// and data objects required to implement the context.
//
// In addition, you can declare debug subcontexts. A subcontext has 
// a parent context; debug messages are generated if the level of the 
// message is <= the subcontext debug level _OR_ <= the parent's debug 
// level. Subcontexts may be nested to any depth. This allows for more
// fine-grained debug levels within class hierarchies.
//
// A subcontext is declared in an .h file (inside class or namespace):
//
//    LocalDebugSubContext;
//
// and implementations are inserted ina  .cc file via:
//
//    InitDebugSubContext(scope,parent_scope,"contextname");
// 

// This macro declares a local debug context within a class or namespace.
#define LocalDebugContext \
  static ::Debug::Context DebugContext; \
  static inline ::Debug::Context & getDebugContext() \
            { return DebugContext; }
// This macro declares a local debug context within a namespace.
#define LocalDebugContext_ns \
  extern ::Debug::Context DebugContext; \
  inline ::Debug::Context & getDebugContext() \
            { return DebugContext; }
// This macro declares a local sub-context within a class or namespace
#define LocalDebugSubContext LocalDebugContext
// This macro declares that this class uses the same context as declared
// in another class or namespace.
#define ImportDebugContext(other) \
  static inline ::Debug::Context & getDebugContext() \
  { return other::getDebugContext(); }
// This macro adds necessary implementation of a local debug context. If you
// declare a local context, then this must be inserted in a .cc file
// somewhere.
#define InitDebugContext(scope,name) \
  ::Debug::Context scope::DebugContext(name)
// This macro adds necessary implementation of a local debug subcontext
#define InitDebugSubContext(scope,parent_scope,name) \
  ::Debug::Context scope::DebugContext(name,&(parent_scope::getDebugContext()))

//
//      =====[ Checking state of debugging contexts ]=====
//      ==================================================
//
// DebugName expands to the name of current context (a const std::string &)
// DebugLevel expands to the debugging level of current context (an int)
//
#define DebugName       (getDebugContext().name())
//
// Debug(level) is True if the debugging level of the current context
// is >= the specified level.
//
#if !LOFAR_DEBUG
#undef DISABLE_DEBUG_OUTPUT 
#define DISABLE_DEBUG_OUTPUT 1
#undef ENABLE_DBGASSERT
#endif

#ifdef DISABLE_DEBUG_OUTPUT
#define DebugLevel   (-1)
#define Debug(level) (false)
#else
#define DebugLevel   (getDebugContext().level())
#define Debug(level) getDebugContext().check(level)
#endif

//      =====[ Generating debugging messages ]=====
//      ===========================================
//
// NB: the macros below make use of some synctatic trickery -- if you use
// them in the body of an if/else statement, make sure you enclose the body
// within {...} to avoid problems.
//
// cdebug(level) 
// cdebug1(level)
//
//    These macros conditionally produce a debugging message on the debugging
//    stream (i.e., stream  only if the current level is >= specified level).
//    Use, e.g.: 
//          cdebug(1)<<"event X, value is "<<value<<std::endl;
//    The normal cdebug() version precedes the message with whatever is
//    returned by a call to sdebug(0). There is a global sdebug() function 
//    (defined in  this file) which simply returns an empty string.
//    The idea here is that classes can redefine sdebug() to generate a 
//    short string identifying the current class and/or object and/or state, 
//    this can make it easier to identify the source of a debugging message
//    (see, e.g., the DMI package for examples of use).
//
//    If for whatever reason you don't want to call sdebug() here, use the
//    cdebug1() macro.
// 
#define cdebug1(level)  if( Debug(level) && Debug::stream_time() ) ::Debug::getDebugStream()
#define cdebug(level)  cdebug1(level)<<sdebug(0)<<": "

//
// dprintf(level) 
// dprintf1(level) 
//
//      These macros conditionally printf a debugging message.
//      Use, e.g.: 
//            dprintf(1)("event X, value is %d",value);
//
//      The difference between dprintf/dprintf1 is just like cdebug/cdebug1.
//
#define dprintf1(level) cdebug1(level)<<Debug::ssprintf
#define dprintf(level) cdebug(level)<<Debug::ssprintf


// Use this macro to write trace output.
// Similar as dprintf, but uses iostream instead of printf.
// Optionally it can be compiled out.
// A trace message is printed if its level is <= the runtime trace level.
// Thus the lower the message level, the more often it gets printed.
#ifdef ENABLE_TRACER
# define TRACER(level,stream) cdebug1(level) << "trace" << level << ": " << stream << std::endl
#else
# define TRACER(level,stream)
#endif
#define TRACER1(stream) TRACER(1,stream)
#define TRACER2(stream) TRACER(2,stream)
#define TRACER3(stream) TRACER(3,stream)
#define TRACER4(stream) TRACER(4,stream)

// Use this macro to write file and line (and possibly function) as well.
#ifdef ENABLE_TRACER
# if defined(HAVE_PRETTY_FUNCTION)
#  define TRACERF(level,stream) cdebug1(level) << "trace" << level << ' ' << __FILE__ << ':' << __LINE__ << '(' << __PRETTY_FUNCTION__ << "): " << stream << std::endl
# elif defined(HAVE_FUNCTION)
#  define TRACERF(level,stream) cdebug1(level) << "trace" << level << ' ' << __FILE__ << ':' << __LINE__ << '(' << __FUNCTION__ << "): " << stream << std::endl
# else
#  define TRACERF(level,stream) cdebug1(level) << "trace" << level << ' ' << __FILE__ << ':' << __LINE__ << ": " << stream << std::endl
# endif
#else
# define TRACERF(level,stream)
#endif
#define TRACERF1(stream) TRACERF(1,stream)
#define TRACERF2(stream) TRACERF(2,stream)
#define TRACERF3(stream) TRACERF(3,stream)
#define TRACERF4(stream) TRACERF(3,stream)

// This macro creates a Tracer object, so you get an automatic trace
// message at the end of a scope.
// objname gives the name of the Tracer object to create.
// Usually only one Tracer object will be used in a scope. In such a case
// the macro TRACERPF can be used (which uses a standard object name).
#ifdef ENABLE_TRACER
# define TRACERPFN_INTERNAL(objname,level,funcName,objPtr,stream) \
    ::Debug::Tracer objname; \
    if( Debug(level) ) { \
      std::ostringstream trace_oss; \
      trace_oss << stream; \
      objname.startMsg (level, __FILE__, __LINE__, \
                        funcName, objPtr, trace_oss.str().c_str()); \
    }
#else
# define TRACERPFN_INTERNAL(objname,level,funcName,objPtr,stream)
#endif

#if defined(HAVE_PRETTY_FUNCTION)
# define TRACERPFN(objname,level,stream) \
     TRACERPFN_INTERNAL(objname,level,__PRETTY_FUNCTION__,0,stream)
#elif defined(HAVE_FUNCTION)
# define TRACERPFN(objname,level,stream) \
     TRACERPFN_INTERNAL(objname,level,__FUNCTION__,0,stream)
#else
# define TRACERPFN(objname,level,stream) \
     TRACERPFN_INTERNAL(objname,level,0,0,stream)
#endif

#define TRACERPFN1(objname,stream) TRACERPFN(objname,1,stream)
#define TRACERPFN2(objname,stream) TRACERPFN(objname,2,stream)
#define TRACERPFN3(objname,stream) TRACERPFN(objname,3,stream)
#define TRACERPFN4(objname,stream) TRACERPFN(objname,4,stream)

#define TRACERPF(level,stream) TRACERPFN(xxx_tmp_tracer_xxx,level,stream)
#define TRACERPF1(stream) TRACERPF(1,stream)
#define TRACERPF2(stream) TRACERPF(2,stream)
#define TRACERPF3(stream) TRACERPF(3,stream)
#define TRACERPF4(stream) TRACERPF(4,stream)


// The SourceFileLine macro creates a string containing the current
// filename and line number.
// The CodeStatus1 macro adds the debug context, plus a message. This is 
// handy for forming error and exception messages.
// If your class defines a "sdebug()" method returning the current object
// status (as string or char *), then use CodeStatus instead, to include 
// sdebug() info in your message.
#if defined(HAVE_PRETTY_FUNCTION)
# define SourceFileLine ::Debug::ssprintf("%s:%d(%s)",__FILE__,__LINE__,__PRETTY_FUNCTION__)
#elif defined(HAVE_FUNCTION)
# define SourceFileLine ::Debug::ssprintf("%s:%d(%s)",__FILE__,__LINE__,__FUNCTION__)
#else
# define SourceFileLine ::Debug::ssprintf("%s:%d",__FILE__,__LINE__)
#endif

#define CodeStatus_nf1(msg) (msg)
#define CodeStatus_nf(msg) ("["+LOFAR::string(sdebug())+"] "+CodeStatus_nf1(msg))

#define CodeStatus1(msg) (std::string(msg))+", at "+ SourceFileLine + ")"
#define CodeStatus(msg) ("["+LOFAR::string(sdebug())+"] "+CodeStatus1(msg))

// This inserts declarations of the sdebug() and debug() methods into your class.
// Use DeclareDebugInfo(virtual) to declare a virtual sdebug().
// Else use DeclareDebugInfo().
// The following method declarations are inserted:
//    [qualifiers] string sdebug ( int detail = 1,const string &prefix = "",
//              const char *name = 0 ) const;
//    const char * debug ( int detail = 1,const string &prefix = "",
//                         const char *name = 0 ) const
//    { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
//
#define Declare_sdebug(qualifiers) qualifiers LOFAR::string sdebug ( int detail = 1,const LOFAR::string &prefix = "",const char *name = 0 ) const; 
#define Declare_debug(qualifiers) qualifiers const char * debug ( int detail = 1,const LOFAR::string &prefix = "",const char *name = 0 ) const { return Debug::staticBuffer(sdebug(detail,prefix,name)); }

// this global definition of sdebug allows the use of cdebug/dprintf macros 
// everywhere
inline LOFAR::string sdebug (int=0) { return ""; };

// The ThrowExc macro throws an exception of the specified type, using
// CodeStatus to add on filename, line, current debugging context, and 
// possible object debug status. 
const char exception_message[] = "\n==================================== EXCEPTION ================================\n";
#define ThrowExc(exc,msg)  { cdebug(1)<<exception_message<<SourceFileLine<<" "<<CodeStatus(msg)<<std::endl; throw(exc(msg,sdebug(),__HERE__)); }
#define ThrowExc1(exc,msg)  { cdebug1(1)<<exception_message<<SourceFileLine<<" "<<CodeStatus1(msg)<<std::endl; throw(exc(msg,__HERE__)); }

// Retain old Throw/Throw1 for compatibility. Throws LOFAR::Exception.
#define Throw(msg)  ThrowExc(LOFAR::Exception,msg)
#define Throw1(msg) ThrowExc1(LOFAR::Exception,msg)

// The Assert macro will Throw an AssertError if condition is FALSE.
#define Assert(cond)  { if( !(cond) ) ThrowExc(::Debug::AssertError,"Assert failed: " #cond); }
#define Assert1(cond)  { if( !(cond) ) ThrowExc1(::Debug::AssertError,"Assert failed: " #cond); }

// The FailWhen macro will Throw a Debug::Fail if condition is TRUE
// Always defined (even with debugging off)
#define FailWhen(cond,msg)  { if( cond ) ThrowExc(::Debug::Fail,msg); }
#define FailWhen1(cond,msg)  { if( cond ) ThrowExc1(::Debug::Fail,msg); }

// The DbgFailWhen macro is like FailWhen, but defined to do nothing if 
// debugging is off.
#ifdef ENABLE_DBGASSERT
# define DbgFailWhen(cond,msg)  FailWhen(cond,msg)
# define DbgFailWhen1(cond,msg)  FailWhen1(cond,msg)
#else
# define DbgFailWhen(cond,msg)  
# define DbgFailWhen1(cond,msg)  
#endif

// The DbgAssert macro is like Assert, but defined to do nothing if 
// debugging is off.
#ifdef ENABLE_DBGASSERT
# define DbgAssert(cond) { if( !(cond) ) ThrowExc(::Debug::AssertError,"DbgAssert failed: " #cond); }
# define DbgAssert1(cond) { if( !(cond) ) ThrowExc1(::Debug::AssertError,"DbgAssert failed: " #cond); }
#else
# define DbgAssert(cond)
# define DbgAssert1(cond)
#endif

// The AssertStr macro makes it possible to put arbitrary data in
// the exception message.
// E.g.
//   AssertStr (n < 10, "value " << n << " exceeds maximum");
#define AssertStr(cond,stream) \
 { if( !(cond) ) { \
     std::ostringstream oss; \
     oss << stream; \
     ThrowExc(::Debug::AssertError,"Assertion `" #cond "' failed: " + oss.str()); \
 }}

// The DbgAssertStr macro is like AssertStr, but
// defined to do nothing if debugging is off.
#ifdef ENABLE_DBGASSERT
# define DbgAssertStr(cond,stream) \
 { if( !(cond) ) { \
     std::ostringstream oss; \
     oss << stream; \
     ThrowExc(::Debug::AssertError,"DbgAssert `" #cond "' failed: " + oss.str()); \
 }}
#else
# define DbgAssertStr(cond,stream)
#endif

// The AssertMsg macro is similar to AssertStr, but it does not
// include source and line number in the message.
// It can be used for generating 'normal' error messages.
#define AssertMsg(cond,stream) \
 { if( !(cond) ) { \
     std::ostringstream oss; \
     oss << stream; \
     ::Debug::getDebugStream()<<oss.str()<<std::endl; \
     throw ::Debug::AssertError(oss.str()); \
 }}



namespace Debug
{
  // Define an exception class for assert errors.
  EXCEPTION_CLASS(AssertError,LOFAR::Exception);

  // Typedef the exception type, so we can change whenever needed.
  //##ModelId=3DB9546401F6
  EXCEPTION_CLASS(Fail,LOFAR::Exception);
  
  extern LOFAR::ostream * dbg_stream_p;
  
  inline LOFAR::ostream & getDebugStream ()
  { return *dbg_stream_p; }

  // sets level of given context
  bool setLevel (const LOFAR::string &context,int level);
      
  // initializes debug levels from command line (looks for options of
  // the form -dContext=#, or -d# for all levels, or filename.debug
  // to load from file, or -dl to load from default progname.debug file)
  void initLevels   (int argc,const char *argv[],bool save=true);
  // saves debug to file (default: progname.debug) 
  bool saveLevels ( LOFAR::string fname = "" );
  // loads debug levels from file (default: progname.debug) 
  void loadLevels ( LOFAR::string fname = "" );
  // redirects debug output to file
  int redirectOutput (const LOFAR::string &fname);

  // copies string into static buffer. Thread-safe (i.e. each thread
  // has its own buffer)
  const char * staticBuffer( const LOFAR::string &str );

  // appends strings and inserts a space, if needed
  LOFAR::string& append( LOFAR::string &str,const LOFAR::string &str2,const LOFAR::string &sep = " " );
  // sprintfs to a string object, returns it
  const LOFAR::string ssprintf( const char *format,... );
  // sprintfs to a string, with append & insertion of spaces
  int appendf( LOFAR::string &str,const char *format,... );
  
  //  // helper functions and declarations
  //  int dbg_printf( const char *format,... );


  //##ModelId=3C21B55E02FC
  class Context 
  {
  public:
    //##ModelId=3C21B594005B
    Context (const LOFAR::string &name, Context *parent_ = 0);

    //##ModelId=3DB95464028D
    ~Context();
    
    //##ModelId=3C21B9750352
    bool check (int level) const;

    //##ModelId=3DB954640293
    int level () const;
    //##ModelId=3DB95464029E
    int setLevel (int value);

    //##ModelId=3DB9546402B5
    const LOFAR::string& name () const;

    //##ModelId=3DB9546402C2
    static void initialize ();
        
  private:
        
    //##ModelId=3DB954640264
    static bool initialized;
    //##ModelId=3C21B57C027D
    int debug_level;
    //##ModelId=3C21B5800193
    LOFAR::string context_name;
    //##ModelId=3CD68637038B
    Context *parent;
  };


  //##ModelId=3C21B9750352
  //## Other Operations (inline)
  inline bool Context::check (int level) const
  {
    if( !initialized )
      return false;
    if( parent && parent->check(level) )
      return true;
    return level <= debug_level;
  }

  //##ModelId=3DB954640293
  inline int Context::level () const
  {
    return debug_level;
  }

  //##ModelId=3DB95464029E
  inline int Context::setLevel (int value)
  {
    debug_level = value;
    return value;
  }

  //##ModelId=3DB9546402B5
  inline const LOFAR::string& Context::name () const
  {
    return context_name;
  }
  
  //##ModelId=3DB9546402C2
  inline void Context::initialize ()
  {
    initialized = true;
  }

#ifdef ENABLE_TRACER
  //##ModelId=3DB954640201
  class Tracer
  {
  public:
    //##ModelId=3DB9546402E2
    Tracer() : itsDo(false) {}

    //##ModelId=3DB9546402E3
    void startMsg (int level,
		   const char* file, int line, const char* func,
		   const char* msg, const void* objPtr);

    //##ModelId=3DB9546402EA
    ~Tracer()
    { if (itsDo) endMsg(); }

  private:
    //##ModelId=3DB9546402EB
    Tracer(const Tracer&);
    //##ModelId=3DB9546402ED
    Tracer& operator= (const Tracer&);
    //##ModelId=3DB9546402EF
    void endMsg();

    //##ModelId=3DB9546402DE
    bool    itsDo;
    //##ModelId=3DB9546402DF
    int     itsLevel;
    //##ModelId=3DB9546402E1
    LOFAR::string  itsMsg;
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
    getDebugStream() << ssprintf("%ld.%06ld ",tv.tv_sec-tv_init.tv_sec,tv.tv_usec);
    return 1;
  }
#else
  inline int printf_time () { return 1; };
  inline int stream_time () { return 1; };
#endif

  extern Context DebugContext;
  inline Context & getDebugContext ()  { return DebugContext; }

} // namespace Debug


// Default DebugContext is the one in Debug.
namespace DebugDefault 
{
  using ::Debug::getDebugContext;
};

// inline functions for converting scalars to strings
inline LOFAR::string num2str (int x)
{
  return Debug::ssprintf("%d",x);
}
inline LOFAR::string num2str (double x)
{
  return Debug::ssprintf("%f",x);
}



#endif
