//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CA045460090.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CA045460090.cm

//## begin module%3CA045460090.cp preserve=no
//## end module%3CA045460090.cp

//## Module: LoggerWP%3CA045460090; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\LoggerWP.cc

//## begin module%3CA045460090.additionalIncludes preserve=no
//## end module%3CA045460090.additionalIncludes

//## begin module%3CA045460090.includes preserve=yes
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
//## end module%3CA045460090.includes

// LoggerWP
#include "OCTOPUSSY/LoggerWP.h"
//## begin module%3CA045460090.declarations preserve=no
//## end module%3CA045460090.declarations

//## begin module%3CA045460090.additionalDeclarations preserve=yes
//## end module%3CA045460090.additionalDeclarations


// Class LoggerWP 

LoggerWP::LoggerWP (int maxlev, int scope)
  //## begin LoggerWP::LoggerWP%3CA0451401B9.hasinit preserve=no
  //## end LoggerWP::LoggerWP%3CA0451401B9.hasinit
  //## begin LoggerWP::LoggerWP%3CA0451401B9.initialization preserve=yes
  : WorkProcess(AidLoggerWP),
    level_(maxlev),consoleLevel_(-1),scope_(scope),fd(-1)
  //## end LoggerWP::LoggerWP%3CA0451401B9.initialization
{
  //## begin LoggerWP::LoggerWP%3CA0451401B9.body preserve=yes
  //## end LoggerWP::LoggerWP%3CA0451401B9.body
}


LoggerWP::~LoggerWP()
{
  //## begin LoggerWP::~LoggerWP%3CA044DE02AB_dest.body preserve=yes
  if( fd >= 0 )
    close(fd);
  //## end LoggerWP::~LoggerWP%3CA044DE02AB_dest.body
}



//## Other Operations (implementation)
void LoggerWP::init ()
{
  //## begin LoggerWP::init%3CA045020054.body preserve=yes
  // default logname is app path
  string filebase = config.appPath()+".log";
  filename_ = filebase;
  // .. but can be overridden by config
  config.get("logfile",filename_);

  // get log levels from config
  config.get("loglev",level_);
  config.get("logcon",consoleLevel_);
  config.getOption("lc",consoleLevel_);
  level_ = max(level_,consoleLevel_);
  
  config.getOption("logscope",scope_);
  
  dprintf(0)("log level: %d, console log level: %d, scope: %d\n",
      level_,consoleLevel_,scope_);

  // subscribe to log messages
  subscribe(MsgLog|AidWildcard,scope_);
  
  // try to open log file and grab a write-lock on it. If that fails, try 
  // "file.1", etc. This ensures that different processes do not write 
  // to the same log.
  for( int filenum = 0; ; filenum++ )
  {
    if( filenum )
      filename_ = filebase + Debug::ssprintf(".%d",filenum);
    
    // try to open the file
    fd = open(filename_.c_str(),O_CREAT|O_WRONLY|O_APPEND,0644);
    if( fd < 0 )
    {
      dprintf(0)("open(%s): %d (%s)\n",filename_.c_str(),errno,strerror(errno));
      dprintf(0)("logging to file disabled\n");
      return;
    }
    // try to set write-lock
    struct flock lock = { F_WRLCK,0,0,1,0 };
    if( fcntl(fd,F_SETLK,&lock) >= 0 )  // break out on success
      break; 
    int err = errno;
    if( fcntl(fd,F_GETLK,&lock) >= 0 )
      dprintf(0)("%s: already in use by pid %d\n",filename_.c_str(),lock.l_pid);
    else
    {
      dprintf(0)("%s: failed to set lock: %s\n",filename_.c_str(),strerror(err));
      dprintf(0)("logging to file disabled\n");
      return;
    }
    close(fd);
  }
  dprintf(0)("opened log file %s\n",filename_.c_str());
  
  // write header record
  string hdr = Debug::ssprintf("%s|logger started, level=%d, scope=%d",
              Timestamp::now().toString("%d/%m/%y").c_str(),level_,scope_);
  struct stat st;
  if( !fstat(fd,&st) && st.st_size > 0 )
    logMessage(address().toString(),"----------------------------------------------",0,LogNormal);
  logMessage(address().toString(),hdr,0,LogNormal);
  //## end LoggerWP::init%3CA045020054.body
}

void LoggerWP::stop ()
{
  //## begin LoggerWP::stop%3CA05A7E01CE.body preserve=yes
  logMessage(address().toString(),"processing remaining messages",0,LogNormal);
  MessageRef mref;
  for(;;)
  {
    dequeue(MsgLog|AidWildcard,&mref);
    if( mref.valid() )
    {
      receive(mref);
      mref.detach();
    }
    else
      break;
  }
  logMessage(address().toString(),"logger stopped",0,LogNormal);
  if( fd >= 0 )
    close(fd);
  fd = -1;
  //## end LoggerWP::stop%3CA05A7E01CE.body
}

int LoggerWP::receive (MessageRef &mref)
{
  //## begin LoggerWP::receive%3CA0450C0103.body preserve=yes
  const Message &msg = mref.deref();
  // process Log messages, but ignore from myself
  if( msg.id()[0] == MsgLog && msg.from() != address() )
  {
    int idlen = msg.id().size();
    AtomicID type = idlen>1 ? msg.id()[1] : LogNormal;
    int lev = idlen>2 ? msg.id()[2].id() : 0;
    // compare to our log level
    if( lev <= level() )
    {
      string str(static_cast<const char*>(msg.data()),msg.datasize() );
      logMessage(msg.from().toString(),str,lev,type);
    }
  }
  return Message::ACCEPT;
  //## end LoggerWP::receive%3CA0450C0103.body
}

void LoggerWP::setScope (int scope)
{
  //## begin LoggerWP::setScope%3CA04AF50212.body preserve=yes
  unsubscribe(MsgLog|AidWildcard);
  subscribe(MsgLog|AidWildcard,scope_=scope);
  //## end LoggerWP::setScope%3CA04AF50212.body
}

void LoggerWP::logMessage (const string &source, const string &msg, int level, AtomicID type)
{
  //## begin LoggerWP::logMessage%3CA04A1F03D7.body preserve=yes
  string out = msg;
  // chop off trailing newlines
  while( out[out.length()-1] == '\n' )
    out.replace(out.length()-1,1,"");
  
  // chop redundancy off the type string
  string ts = type.toString();
  if( ts.compare("Log",0,3) )
    ts = ts.substr(3);
  
  // form full output record
  out =  Timestamp::now().toString("%T|") + 
         source + "|" + ts + Debug::ssprintf("|%d|",level) +
         ( out.length() ? out : string("{null message}") ) + "\n";

  // log to console
  if( level <= consoleLevel() )
    cerr<<">>>"<<out;

  // log to file
  if( fd < 0 )
    return;
  int res = write(fd,out.data(),out.length());
  if( res<0 )
  {
    dprintf(0)("error writing to log file: %d (%s)\n",errno,strerror(errno));
  }
  else if( res < (int)out.length() )
  {
    dprintf(0)("error writing to log file: only %d of %d bytes written\n",res,out.length());
  }
  //## end LoggerWP::logMessage%3CA04A1F03D7.body
}

// Additional Declarations
  //## begin LoggerWP%3CA044DE02AB.declarations preserve=yes
  //## end LoggerWP%3CA044DE02AB.declarations

//## begin module%3CA045460090.epilog preserve=yes
//## end module%3CA045460090.epilog
