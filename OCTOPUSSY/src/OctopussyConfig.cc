//##ModelId=3DB936CB00A9
//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CD0078A01F1.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CD0078A01F1.cm

//## begin module%3CD0078A01F1.cp preserve=no
//## end module%3CD0078A01F1.cp

//## Module: OctopussyConfig%3CD0078A01F1; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\OctopussyConfig.cc

//## begin module%3CD0078A01F1.additionalIncludes preserve=no
//## end module%3CD0078A01F1.additionalIncludes

//## begin module%3CD0078A01F1.includes preserve=yes
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
//## end module%3CD0078A01F1.includes

// OctopussyConfig
#include "OCTOPUSSY/OctopussyConfig.h"
//## begin module%3CD0078A01F1.declarations preserve=no
//## end module%3CD0078A01F1.declarations

//## begin module%3CD0078A01F1.additionalDeclarations preserve=yes
OctopussyConfig 
    OctopussyConfig::global_( getenv("HOME") + string("/.octopussy") );
//##ModelId=3CD005FD01DC
//## end module%3CD0078A01F1.additionalDeclarations


// Class OctopussyConfig 

OctopussyConfig::OctopussyConfig (const string &confdir)
  //## begin OctopussyConfig::OctopussyConfig%3CD005FD01DC.hasinit preserve=no
  //## end OctopussyConfig::OctopussyConfig%3CD005FD01DC.hasinit
  //## begin OctopussyConfig::OctopussyConfig%3CD005FD01DC.initialization preserve=yes
    : configdir(confdir)
  //## end OctopussyConfig::OctopussyConfig%3CD005FD01DC.initialization
{
  //## begin OctopussyConfig::OctopussyConfig%3CD005FD01DC.body preserve=yes
  //## end OctopussyConfig::OctopussyConfig%3CD005FD01DC.body
}



//##ModelId=3CD0060C00A7
//## Other Operations (implementation)
void OctopussyConfig::init (int argc, const char **argv)
{
  //## begin OctopussyConfig::init%3CD0060C00A7.body preserve=yes
  if( configdir[configdir.length()-1] != '/' )
    configdir += '/';
  
  // set command line
  string localfile;
  args_.resize(argc);
  for( int i=0; i<argc; i++ )
  {
    args_[i] = argv[i];
    if( args_[i].length() > 5 && args_[i].substr(args_[i].length()-5) == ".conf" )
      localfile = args_[i];
  }
  
  // determine config filenames
  // global config file:
  string globalfile = "octopussy.conf";
  // set hostname and host-specific config file:
  char hname[1024];
  FailWhen(gethostname(hname,sizeof(hname))<0,"gethostname(): "+string(strerror(errno)));
  fullHostname_ = hname;
  // strip off domain name, if needed
  size_t pos = fullHostname_.find_first_of('.');
  if( pos != string::npos )
    hostname_ = fullHostname_.substr(0,pos);
  else
    hostname_ = fullHostname_;
  string hostfile = hostname_+".conf";
  
  // appName_ and app-specific config file:
  string progfile;
  if( argc )
  {
    appPath_ = argv[0];
    size_t pos = appPath_.find_last_of('/');
    if( pos != string::npos )
      appName_ = appPath_.substr(pos+1);
    else
      appName_ = appPath_;
    progfile += appName_ + ".conf";
  }
  // now, load files from global directory first
  merge(configdir + globalfile,True,True);
  merge(configdir + hostfile,True,True);
  if( progfile.length() )
    merge(configdir + progfile,True,True);
  // merge in (and override) with local config files, if any
  merge(globalfile,True,True);
  merge(hostfile,True,True);
  if( progfile.length() )
    merge( progfile,True,True);
  // merge in local file, if specified
  if( localfile.length() )
    merge( localfile,True,True);
  // finally, merge in command line
  merge(args_,True);
  
  dprintf(0)("%d entries configured\n",config().size());
  if( Debug(3) )
  {
    for( CCMI iter = config().begin(); iter != config().end(); iter++ )
      dprintf(3)("entry %s=%s\n",iter->first.c_str(),iter->second.c_str());
  }
  //## end OctopussyConfig::init%3CD0060C00A7.body
}

//##ModelId=3CD0061B0258
bool OctopussyConfig::getOption (const string &name) const
{
  //## begin OctopussyConfig::getOption%3CD0061B0258.body preserve=yes
  string dum;
  return getOption(name,dum);
  //## end OctopussyConfig::getOption%3CD0061B0258.body
}

//##ModelId=3CD0063503BD
bool OctopussyConfig::getOption (const string &name, int &value) const
{
  //## begin OctopussyConfig::getOption%3CD0063503BD.body preserve=yes
  string val;
  if( !getOption(name,val) )
    return False;
  value = atoi(val.c_str());
  return True;
  //## end OctopussyConfig::getOption%3CD0063503BD.body
}

//##ModelId=3CD006460137
bool OctopussyConfig::getOption (string name, string &value) const
{
  //## begin OctopussyConfig::getOption%3CD006460137.body preserve=yes
  if( name[0] != '-' )
    name = '-' + name;
  
  for( int i=1; i < argc(); i++ )
  {
//    if( !argv(i).compare(name,0,name.length()) )
    if( !argv(i)._strcompare(0,name.length(),name) )
    {
      // specified as "-ovalue"
      if( argv(i).length() > name.length() )
        value = argv(i).substr(name.length());
      // specified as "-o value"
      else if( i < argc()-1 )
        value = argv(i+1);
      else
        value = "";
      return True;
    }
  }
  return False;
  //## end OctopussyConfig::getOption%3CD006460137.body
}

// Additional Declarations
  //## begin OctopussyConfig%3CD00368038B.declarations preserve=yes
  //## end OctopussyConfig%3CD00368038B.declarations

//## begin module%3CD0078A01F1.epilog preserve=yes
//## end module%3CD0078A01F1.epilog
