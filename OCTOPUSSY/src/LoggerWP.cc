#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

#include "LoggerWP.h"
#include "AppRegistry.h"

  static int dum = LoggerWP::registerApp();
        
int LoggerWP::registerApp ()
{
  AppRegistry::registerApp(AidLoggerWP,constructor);
  return 0;
}

WPRef LoggerWP::constructor (DataRecord::Ref &initrecord)
{
  int maxlev = 9999;
  int scope = Message::GLOBAL;
  if( initrecord.valid() )
  {
    const DataRecord &rec = *initrecord;
    maxlev = rec[AidMax|AidLevel].as<int>(maxlev);
    if( rec[AidScope].exists() )
      if( rec[AidScope].type() == Tpstring )
      {
        const string &str = rec[AidScope].as<string>();
        if( str == "GLOBAL" )
          scope = Message::GLOBAL;
        else if( str == "HOST" )
          scope = Message::HOST;
        else if( str == "LOCAL" )
          scope = Message::LOCAL;
      }
      else
        scope = rec[AidScope].as<int>();
  }
  return WPRef(new LoggerWP(maxlev,scope),DMI::ANONWR);
}



LoggerWP::LoggerWP (int maxlev, int scope)
        : WorkProcess(AidLoggerWP),
    level_(maxlev),consoleLevel_(-1),scope_(scope),fd(-1)
{
}


//##ModelId=3DB9369A0073
LoggerWP::~LoggerWP()
{
  if( fd >= 0 )
    close(fd);
}



//##ModelId=3CA045020054
void LoggerWP::init ()
{
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
  }

//##ModelId=3CA05A7E01CE
void LoggerWP::stop ()
{
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
}

//##ModelId=3CA0450C0103
int LoggerWP::receive (MessageRef &mref)
{
  const Message &msg = mref.deref();
  // process Log messages, but ignore from myself
  if( msg.id()[0] == MsgLog && msg.from() != address() && 
      msg.payloadType() == TpDataRecord )
  {
    AtomicID type = msg[AidType].as<AtomicID>(LogNormal);
    int lev = msg[AidLevel].as<int>(0);
    // compare to our log level
    if( lev <= level() )
    {
      const string &str = msg[AidText].as<string>();
      logMessage(msg.from().toString(),str,lev,type);
    }
  }
  return Message::ACCEPT;
}

//##ModelId=3CA04AF50212
void LoggerWP::setScope (int scope)
{
  unsubscribe(MsgLog|AidWildcard);
  subscribe(MsgLog|AidWildcard,scope_=scope);
}

//##ModelId=3CA04A1F03D7
void LoggerWP::logMessage (const string &source, const string &msg, int level, AtomicID type)
{
  string out = msg;
  // chop off trailing newlines
  while( out[out.length()-1] == '\n' )
    out.replace(out.length()-1,1,"");
  
  // chop redundancy off the type string
  string ts = type.toString();
  if( ts._strcompare(0,3,"Log") )
//  if( ts.compare("Log",0,3) )
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
}
    
