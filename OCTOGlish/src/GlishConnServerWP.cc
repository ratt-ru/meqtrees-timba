#include "GlishConnServerWP.h"
#include "GlishThreadWP.h"

#include <Common/StringUtil.h>
#include <aips/Glish.h>

#include <pwd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

    
using LOFAR::StringUtil;

InitDebugContext(GlishConnServerWP,"GlishServ");

// timeout value for a retry of bind, in seconds
const Timeval Timeout_Retry(10.0),
// re-advertise timeout, in seconds
      Timeout_Advertise(10.0);
// max retries
const int MaxOpenRetries = 10;

using Debug::ssprintf;

// Class GlishConnServerWP 

std::string errno2string (int err)
{
  char errstr[1024];
  if( strerror_r(err,errstr,sizeof(errstr)) == 0 )
    return ssprintf("%d (%s)",err,errstr);
  else
    return ssprintf("%d (strerror_r error: %d)",err,errno);
}

GlishConnServerWP::GlishConnServerWP (string path)
  : WorkProcess(AidGlishConnServerWP)
{
  if( path.empty() )
  {
    // get path from config if not specified explicitly
    config.get("glishconnpath",path,"/tmp/octoglish-%U");
    // if hostname contains a "%U" string, replace with uid
    uint pos0;
    while( (pos0 = path.find_first_of("%U")) != string::npos )
    {
      string uname = getpwuid(getuid())->pw_name;
      path = path.substr(0,pos0) + uname + path.substr(pos0+2);
    }
  }
  cdebug(1)<<"using path "<<path<<" to listen for Glish connections\n";
  connpath_ = path;
  connfd_ =  -1;
  created_ = false;
}

GlishConnServerWP::~GlishConnServerWP()
{
  if( connfd_>=0 )
    close(connfd_);
}

void GlishConnServerWP::init ()
{
  while( connfd_<0 )
  {
    connfd_ = open(connpath_.c_str(),O_RDONLY|O_NONBLOCK);
    if( connfd_ < 0 )
    {
      // if no such file, try to create the pipe
      if( errno == ENOENT )
      {
        if( !mknod(connpath_.c_str(),0600|S_IFIFO,0) )
        {
          cdebug(1)<<"mknod("<<connpath_<<",S_IFIFO): success\n";
          created_ = true;
          continue;
        }
        else
        {
          cdebug(1)<<"mknod("<<connpath_<<"): "<<errno2string(errno)<<endl;
          break;
        }
      }
      else
      {
      // other error
        cdebug(1)<<"open("<<connpath_<<"): "<<errno2string(errno)<<endl;
        break;
      }
    }
    else
    {
      cdebug(1)<<"open("<<connpath_<<"): success, fd="<<connfd_<<endl;
      cout<<"[PIPE]"<<connpath_<<"[/PIPE]\n";
    }
  }
  // opened successfully, or gave up
}

bool GlishConnServerWP::start ()
{
  WorkProcess::start();
  // if file not opened, shut down immediately
  if( connfd_ < 0 )
  {
    cdebug(1)<<"pipe not open, detaching outselves\n";
    detachMyself();
  }
  else
    addInput(connfd_,EV_FDREAD);
  bufpos_ = 0;
  return false;
}

void GlishConnServerWP::stop ()
{
  WorkProcess::stop();
  if( connfd_>=0 )
  {
    cdebug(1)<<"closing "<<connpath_<<"\n";
    close(connfd_);
    connfd_ = -1;
  }
  if( created_ )
  {
    cdebug(1)<<"deleting "<<connpath_<<"\n";
    unlink(connpath_.c_str());
    created_ = false;
  }
}

int GlishConnServerWP::input (int , int )
{
  for( ;; )
  {
    // read description of incoming connection
    int nb = read(connfd_,readbuf_+bufpos_,sizeof(readbuf_)-bufpos_);
    //
    if( nb<0 )
    {
      if( errno == EAGAIN || errno == EINTR )
        return Message::ACCEPT;
      cdebug(1)<<"read("<<connpath_<<"): "<<errno2string(errno)<<", closing\n";
      detachMyself();
      return Message::CANCEL;
    }
    else if( nb==0 )
    {
      cdebug(1)<<"read("<<connpath_<<"): 0 (EOF), closing\n";
      detachMyself();
      return Message::CANCEL;
    }
    // at this point, we've got bufpos_+nb bytes in the buffer
    bufpos_ += nb;
    string input(readbuf_,bufpos_);
    // find the start tag
    const string start_tag = "[CONNECTION]";
    const string end_tag = "[/CONNECTION]";
    uint i0 = input.find(start_tag);
    if( i0 == string::npos )
    {
      uint i1 = input.rfind("[");
      if( i1 == string::npos )
      {
        cdebug(1)<<": no start tag found in input, flushing all\n";
        bufpos_ = 0;
      }
      else
      {
        cdebug(1)<<": no start tag found in input, flushing "<<i1<<" chars\n";
        input.copy(readbuf_,string::npos,i1);
        bufpos_ -= i1;
      }
      return Message::ACCEPT;
    }
    // find the end tag
    uint i1 = input.find(end_tag,i0);
    if( i1 == string::npos )
    {
      cdebug(2)<<": no end tag found, waiting for more input\n";
      if( i0>0 )
      {
        cdebug(2)<<": flushing "<<i0<<" chars prior to start tag\n";
        input.copy(readbuf_,string::npos,i0);
        bufpos_ -= i0;
      }
    }
    bufpos_ = 0;
    // all found, extract argument array. Strip off start and end tags first
    input = input.substr(i0+start_tag.length(),i1-i0-start_tag.length());
    // split input uinto two sections (for two agents)
    vector<string> sections = StringUtil::split(input,'\n');
    if( sections.size() != 2 )
    {
      cdebug(2)<<": malformed input (!=2 sections), ignoring\n";
      return Message::ACCEPT;
    }
    cdebug(3)<<": creating agents\n";
    cdebug(3)<<": "<<sections[0]<<endl;
    cdebug(3)<<": "<<sections[1]<<endl;
    // create the two agents
    vector<string> args1 = StringUtil::split(sections[0],'\t');
    vector<string> args2 = StringUtil::split(sections[1],'\t');
    GlishSysEventSource 
      *evsrc1 = makeEventSource(args1),
      *evsrc2 = makeEventSource(args2);
    // create new WP 
    attachWP(new GlishThreadedClientWP(evsrc1,evsrc2,false),DMI::ANONWR);
  }
}

GlishSysEventSource * GlishConnServerWP::makeEventSource(vector<string> &args)
{
  int argc = args.size();
  const char * argv[argc];
  for( int i=0; i<argc; i++ )
    argv[i] = args[i].c_str();
  // stupid glish wants non-const argv
  return new GlishSysEventSource(argc,const_cast<char**>(argv));
}


