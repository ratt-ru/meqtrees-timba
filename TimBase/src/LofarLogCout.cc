//#  filename.cc: one line description
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include <Common/LofarLogCout.h>
#include <Common/lofar_fstream.h>
#include <cstdarg>
#include <sys/time.h>


namespace LOFAR {

namespace LFDebug 
{
  // -----------------------------------------------------------------------
  // various globals
  // -----------------------------------------------------------------------
  // default debug context
  Context DebugContext("Global");

  bool Context::initialized = false;

  // debug output stream -- same as cerr on startup
  ostream * dbg_stream_p = &cerr;
  ofstream dbg_file;

  // timestamp
  struct timeval tv_init;
  int dum_tv_init = gettimeofday(&tv_init,0);

  // -----------------------------------------------------------------------
  // debug contexts and levels
  // -----------------------------------------------------------------------
  // map of currently set debug levels  
  //##ModelId=3DB954640131
  typedef map<string,int> DebugLevelMap;
  //##ModelId=3DB954640128
  typedef DebugLevelMap::iterator DLMI;
  //##ModelId=3DB954640105
  typedef DebugLevelMap::const_iterator CDLMI;
  DebugLevelMap *levels = 0;

  // map of debug contexts present in program
  //##ModelId=3DB95464011F
  typedef multimap<string,Context*> ContextMap;
  //##ModelId=3DB95464010E
  typedef ContextMap::iterator CMI;
  //##ModelId=3DB9546400FB
  typedef ContextMap::const_iterator CCMI;
  ContextMap *contexts = 0;

  // executable name
  string progname;

  // special debug level sets everything
  const string Everything("Everything");

  // -----------------------------------------------------------------------
  // setLevel("context",level)
  // sets level of specific context (or Everything, if context is zero-length)
  // -----------------------------------------------------------------------
  bool setLevel ( const string &contxt,int level )
  {
    if( !levels )
      levels = new DebugLevelMap;
    (*levels)[contxt.length() ? contxt : Everything] = level;

    pair<CMI,CMI> range(contexts->begin(),contexts->end());
    // specific context specified?
    if( contxt.length() && contxt != Everything )
    {
      // lookup context
      range = contexts->equal_range(contxt);
      if( range.first == contexts->end() )
      {
        cerr<<"Debug: unknown context '"<<contxt<<"'\n";
        return false;
      }
      cerr<<"Debug: setting debug level "<<contxt<<"="<<level<<endl;
    }
    else // set all contexts
    {
      cerr<<"Debug: setting all debug levels to "<<level<<endl;
    }
    // set levels in range
    for( CMI iter = range.first; iter != range.second; iter++ )
    {
      (*levels)[iter->first] = level;
      iter->second->setLevel( level );
    }
    return true;
  }

  // -----------------------------------------------------------------------
  // initLevels()
  // parses command-line arguments and initializes debug levels, etc.
  // -----------------------------------------------------------------------
  void initLevels (const string& fname)
  {
    Context::initialize();
    if( !contexts )
    {
      cerr<<"initLevels: warning: context map not initialized\n";
      return;
    }
    loadLevels (fname);
  }

  // -----------------------------------------------------------------------
  // loadLevels(fname)
  // loads debug levels from file, or "progname.debug" by default
  // -----------------------------------------------------------------------
  void loadLevels (const string& fname )
  {
    FILE *f = fopen(fname.c_str(),"rt");
    if( !f )
    {
      cerr<<"Debug::loadLevels: error opening "<<fname<<endl;
      return;
    }
    cerr<<"Debug: loading levels from file "<<fname<<endl;
    while( !feof(f) )
    {
      char line[1024];
      line[0]=0;
      if( !fgets(line,sizeof(line),f) )
        break;
      char context[1024];
      int level;
      if( sscanf(line,"%s %d",context,&level)<2 )
      {
        cerr<<"Debug: ignoring line: "<<line;
        continue;
      }
      setLevel(context,level);
    }
    fclose(f);
  }

  // -----------------------------------------------------------------------
  // Context
  // Context class implementation
  // -----------------------------------------------------------------------
  Context::Context (const string &name, Context *parent_)
    : debug_level(0),context_name(name),parent(parent_)
  {
    if( parent == this )
    {
      cerr<<"Debug: context "<<name<<" is its own parent, aborting"<<endl;
      abort();
    }
    if( !contexts ) // allocate on first use
      contexts = new ContextMap;
    // insert into context map
    bool newcontext = contexts->find(name) == contexts->end();
    contexts->insert( ContextMap::value_type(name,this) );
    // look into preset levels
    int lev = 0;
    if( levels )
    {
      // set to the overall level first, if specified
      CDLMI iter = levels->find("Everything");
      if( iter != levels->end() )
        lev = iter->second;
      // set to the specific level, if specifield
      iter = levels->find(name);
      if( iter != levels->end() )
        lev = iter->second;
    }
    setLevel(lev);
#ifndef DISABLE_DEBUG_OUTPUT
    if( newcontext ) 
      cerr<<"Debug: registered context "<<name<<"="<<lev<<"\n";
#endif
    //## end Debug::Context::Context%3C21B594005B.body
  }


  Context::~Context()
  {
    if( !contexts )
      return;

    for( CMI iter = contexts->begin(); iter != contexts->end(); ) {
      if( iter->second == this ) {
        contexts->erase(iter++);
      } else {
        iter++;
      }
    }

    if( contexts->empty() )
    {
      delete contexts;
      contexts = 0;
    }
  }

  // int dbg_printf( const char *format, ...) 
  // {
  //   va_list ap;
  //   va_start(ap,format);
  //   int ret = vfprintf(stderr,format,ap);
  //   va_end(ap);
  //   return ret;
  // }
  // 

  // -----------------------------------------------------------------------
  // ssprintf
  // Like sprintf, but returns an string with the output
  // -----------------------------------------------------------------------
  const string ssprintf( const char *format,... )
  {
    char tmp_cstring[1024]="";
    va_list ap;
    va_start(ap,format);
    vsnprintf(tmp_cstring,sizeof(tmp_cstring),format,ap);
    va_end(ap);
    return string(tmp_cstring);
  }

  // -----------------------------------------------------------------------
  // append
  // appends strings and inserts a separator, if needed
  // -----------------------------------------------------------------------
  string& append( string &str,const string &str2,const string &sep )
  {
    int len = str.length(),len2 = str2.length(),lensep = sep.length();
    if( lensep )
    {
      if( len >= lensep && len2 >= lensep && 
          str.substr(len-lensep,lensep) != sep &&
          str2.substr(0,lensep) != sep  )
        str += sep;
    }
    return str += str2;
  }

  // -----------------------------------------------------------------------
  // appendf
  // sprintfs to a string, with append, and include a space if needed
  // -----------------------------------------------------------------------
  int appendf( string &str,const char *format,... )
  {
    char tmp_cstring[1024]="";
    va_list ap;
    va_start(ap,format);
    int ret = vsnprintf(tmp_cstring,sizeof(tmp_cstring),format,ap);
    va_end(ap);
    append(str,tmp_cstring);
    return ret;
  }


#ifdef ENABLE_TRACER
  // -----------------------------------------------------------------------
  // Tracer
  // Tracer class implementation
  // -----------------------------------------------------------------------


  void Tracer::startMsg (int level, const char* file, int line,
                         const char* func, const char* msg,
                         const void* objPtr)
  {
    itsDo    = true;
    itsLevel = level;
    ostringstream oss;
    if (file != 0) {
      oss << file << ':' << line;
    }
    if (func != 0) {
      oss << ' ' << func;
    }
    if (objPtr != 0) {
      oss << " this=" << objPtr;
    }
    if (msg != 0) {
      oss << ": " << msg;
    }
    itsMsg = oss.str();
    getDebugStream() << "TRACE" << itsLevel << " start " << itsMsg << endl;
  }

  void Tracer::endMsg()
  {
    getDebugStream() << "TRACE" << itsLevel << " end " << itsMsg << endl;
    //    delete [] itsMsg;
    //     itsMsg = 0;
  }
#endif

} // namespace LFDebug

}
