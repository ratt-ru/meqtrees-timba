//  Debug.cc:
//
//  Copyright (C) 2002
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

//#
//# DO NOT INCLUDE ANY HEADER FILES IN THIS SOURCE FILE. THIS FILE CONTAINS
//# COMMON CODE THAT WILL BE INCLUDED BY OTHER SOURCE FILES.
//#

namespace Debug 
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

#ifdef USE_THREADS
  pthread_mutex_t levels_mutex = PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP;
#define lockMutex(t) ::LOFAR::Thread::Mutex::Lock _##t##_lock(t##_mutex)
#else
#define lockMutex(t) 
#endif

  // executable name
  string progname;

  // special debug level sets everything
  const string Everything("Everything");

  // -----------------------------------------------------------------------
  // staticBuffer(str)
  // copies an string into a static buffer, return char *.
  // This is thread-safe
  // -----------------------------------------------------------------------
#ifdef USE_THREADS
  void _delete_char_array (void *array)
  { delete [] static_cast<char*>(array); }

  ::LOFAR::Thread::Key static_buf(_delete_char_array);
#endif

  // returns a thread-specifc static buffer (for debug() calls)
  const char * staticBuffer( const string &str )
  {
    const size_t bufsize = 1024;
#ifdef USE_THREADS
    char * buffer = static_cast<char*>(static_buf.get()); 
    if( !buffer )
      static_buf.set(buffer = new char[bufsize]);
#else
    static char buffer[bufsize];
#endif
    buffer[ str.copy(buffer,bufsize-1) ] =0;
    return buffer;
  }

  // -----------------------------------------------------------------------
  // setLevel("context",level)
  // sets level of specific context (or Everything, if context is zero-length)
  // -----------------------------------------------------------------------
  bool setLevel ( const string &contxt,int level )
  {
    lockMutex(levels);
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
  // setLevel(str)
  // parses level specification of the form "context=level", and calls
  // setLevel on it. If just "level" is specified, sets everything
  // -----------------------------------------------------------------------
  bool setLevel ( const string &str )
  {
    lockMutex(levels);
    string contxt;
    string level;
    size_t j = str.find('=');
    if( j == str.npos ) {
      level = str;
    } else {
      contxt = str.substr(0,j);
      level = str.substr(j+1);
    }
    if( !level.length() ) 
    {
      cerr<<"Illegal debug level specification\nValid specifications are: ";
      string ctxt0;
      for( ContextMap::const_iterator iter = contexts->begin();
           iter != contexts->end(); iter++ ) 
      {
        if( iter->first != ctxt0 ) 
        {
          cerr<<"  -d"<<(ctxt0 = iter->first)<<"=<level>\n";
        }
      }
      cerr<<"  -d<level>";
      exit(1);
    }
    setLevel(contxt,atoi(level.c_str()));
    return true;
  }

  // -----------------------------------------------------------------------
  // redirectOutput
  // redirects the debug output to a file. If fname is empty, uses cerr.
  // -----------------------------------------------------------------------
  int redirectOutput (const string &fname)
  {
    if( fname.empty() )
    {
      cerr<<"Debug: output directed to standard error stream\n";
      dbg_stream_p = &cerr;
    }
    else
    {
      dbg_file.open(fname.c_str());
      if( !dbg_file )
      {
        cerr<<"Debug: error opening output file: "<<fname<<endl;
        return 0;
      }
      else
      {
        dbg_stream_p = &dbg_file;
        cerr<<"Debug: output directed into file "<<fname<<endl;
      }
    }
    return 1;
  }

  // -----------------------------------------------------------------------
  // initLevels(argc,argv,save)
  // parses command-line arguments and initializes debug levels, etc.
  // -----------------------------------------------------------------------
  void initLevels ( int argc,const char *argv[],bool save )
  {
    lockMutex(levels);
    Context::initialize();
    bool changed = false;
    progname = argv[0];
    if( !contexts )
    {
      cerr<<"initLevels: warning: context map not initialized\n";
      return;
    }
    // scan command line
    for( int i=1; i<argc; i++ )
    {
      string str( argv[i] );
      // look for arguments ending with ".debug", and load level file
      const string ext = ".debug";
      if( str.length() >= ext.length() && str.substr(str.length()-ext.length()) == ext )
      {
        changed = false;
        loadLevels(str);
      }
      // "-dl": load default file
      else if( str.substr(0,3) == string("-dl") )
      {
        changed = false;
        loadLevels();
      }
      // "-d:filename": redirect debug output to file
      else if( str.substr(0,3) == string("-d:") )
      {
        redirectOutput(str.substr(3));
      }
      // "-dxxx": debug level specification
      else if( str.substr(0,2) == string("-d") )
      {
        changed = true;
        setLevel( str.substr(2) );
      }
    }
    if( save && changed )
      saveLevels();
  }

  // -----------------------------------------------------------------------
  // saveLevels(fname)
  // saves debug levels to file "fname.debug"
  // if fname is empty, uses the erxecutable's names
  // -----------------------------------------------------------------------
  bool saveLevels ( string fname )
  {
    lockMutex(levels);
    if( !fname.length() )
    {
      if( !progname.length() )
      {
        cerr<<"Debug::loadLevels: you must call initLevels() first\n";
        exit(1);
      }
      fname = progname+".debug";
    }
    if( !levels )
    {
      cerr<<"Debug::saveLevels: no levels have been set"<<endl;
      return false;
    }
    FILE *f = fopen(fname.c_str(),"wt");
    if( !f )
    {
      cerr<<"Debug::saveLevels: error opening "<<fname<<endl;
      return false;
    }
    // make sure "Everything" goes in first
    CDLMI iter = levels->find(Everything);
    if( iter != levels->end() )
      fprintf(f,"%s %d\n",iter->first.c_str(),iter->second);
    for( CDLMI iter = levels->begin(); iter != levels->end(); iter++ )
      if( iter->first != Everything )
        fprintf(f,"%s %d\n",iter->first.c_str(),iter->second);
    fclose(f);
    cerr<<"Debug: "<<levels->size()<<" level(s) saved to "<<fname<<endl;
    return true;
  }

  // -----------------------------------------------------------------------
  // loadLevels(fname)
  // loads debug levels from file, or "progname.debug" by default
  // -----------------------------------------------------------------------
  void loadLevels ( string fname )
  {
    lockMutex(levels);
    if( !fname.length() )
    {
      if( !progname.length() )
      {
        cerr<<"Debug::loadLevels: you must call initLevels() first\n";
        exit(1);
      }
      fname = progname+".debug";
    }
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
    lockMutex(levels);
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
    lockMutex(levels);
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

} // namespace Debug
