//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CCFFF3301FC.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CCFFF3301FC.cm

//## begin module%3CCFFF3301FC.cp preserve=no
//## end module%3CCFFF3301FC.cp

//## Module: ConfigMgr%3CCFFF3301FC; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\ConfigMgr.cc

//## begin module%3CCFFF3301FC.additionalIncludes preserve=no
//## end module%3CCFFF3301FC.additionalIncludes

//## begin module%3CCFFF3301FC.includes preserve=yes
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <time.h>
//## end module%3CCFFF3301FC.includes

// ConfigMgr
#include "DMI/ConfigMgr.h"
//## begin module%3CCFFF3301FC.declarations preserve=no
//## end module%3CCFFF3301FC.declarations

//## begin module%3CCFFF3301FC.additionalDeclarations preserve=yes
InitDebugSubContext(ConfigMgr,DMI,"Config");
//## end module%3CCFFF3301FC.additionalDeclarations


// Class ConfigMgr 

ConfigMgr::ConfigMgr (const string& fname, bool nothrow)
  //## begin ConfigMgr::ConfigMgr%EA0590B8FEED.hasinit preserve=no
  //## end ConfigMgr::ConfigMgr%EA0590B8FEED.hasinit
  //## begin ConfigMgr::ConfigMgr%EA0590B8FEED.initialization preserve=yes
  //## end ConfigMgr::ConfigMgr%EA0590B8FEED.initialization
{
  //## begin ConfigMgr::ConfigMgr%EA0590B8FEED.body preserve=yes
  if( fname.length() )
    load(fname,nothrow);
  //## end ConfigMgr::ConfigMgr%EA0590B8FEED.body
}



//## Other Operations (implementation)
int ConfigMgr::size () const
{
  //## begin ConfigMgr::size%0778FED4FEED.body preserve=yes
  return config_.size();
  //## end ConfigMgr::size%0778FED4FEED.body
}

void ConfigMgr::clear ()
{
  //## begin ConfigMgr::clear%6B6C3E18FEED.body preserve=yes
  config_.clear();
  //## end ConfigMgr::clear%6B6C3E18FEED.body
}

void ConfigMgr::load (const string& fname, bool nothrow)
{
  //## begin ConfigMgr::load%C0C4E648FEED.body preserve=yes
  clear();
  merge(filename=fname,True,nothrow);
  //## end ConfigMgr::load%C0C4E648FEED.body
}

bool ConfigMgr::save (string fname, bool nothrow)
{
  //## begin ConfigMgr::save%80D7E19EFEED.body preserve=yes
  // empty file means use current filename
  if( !fname.length() )
  {
    fname = filename;
    if( !fname.length() )
      if( nothrow )
        return False;
      else
        Throw("ConfigMgr::save(): null filename");
  }
  FILE *f = fopen(fname.c_str(),"wt");
  if( !f )
    if( nothrow )
      return False;
    else
      Throw("open("+fname+"): "+strerror(errno));
  time_t tm = time(0);
  fprintf(f,"# configuration saved on %s\n",ctime(&tm));
  for( CCMI iter = config_.begin(); iter != config_.end(); iter++ )
    fprintf(f,"%s %s\n",iter->first.c_str(),iter->second.c_str());
  fclose(f);
  dprintf(2)("%d config_ entries saved to %s\n",config_.size(),fname.c_str());
  return True;
  //## end ConfigMgr::save%80D7E19EFEED.body
}

bool ConfigMgr::merge (const string& fname, bool override, bool nothrow)
{
  //## begin ConfigMgr::merge%B4793134FEED.body preserve=yes
  FILE *f = fopen(fname.c_str(),"rt");
  if( !f )
  {
    if( nothrow )
    {
      dprintf(2)("merge: can't open file %s (%s)\n",fname.c_str(),strerror(errno));
      return False;
    }
    else
      Throw("open("+fname+"): "+strerror(errno));
  }
  int nread=0,nused=0;
  dprintf(4)("reading config_ file %s\n",fname.c_str());
  while( !feof(f) )
  {
    char s[1024];
    s[0] = 0;
    fgets(s,sizeof(s),f);
    s[sizeof(s)-1] = 0;
    if( !s[0] )
      continue;
    if( s[strlen(s)-1] == '\n' )
      s[strlen(s)-1] = 0;
    // find first non-space
    char *s0 = s;
    while( *s0 && isspace(*s0) )
      s0++;
    // skip comments and empty lines
    if( !*s0 || *s0 == '#' )
      continue;
    // find next space
    char *s1 = strchr(s0,' ');
    if( !s1 )
      continue;
    *s1++ = 0; // s1 now points at start of argument
    // skip whitespace
    while( *s1 && isspace(*s1) )
      s1++;
    // convert into items
    string name = s0,value = s1;
    dprintf(4)("read %s = '%s'\n",s0,s1);
    nread++;
    if( override || config_.find(name) == config_.end() )
    {
      nused++;
      config_[name] = value;
    }
  }
  fclose(f);
  dprintf(2)("%d/%d config_ entries read from %s\n",nread,nused,fname.c_str());
  return True;
  //## end ConfigMgr::merge%B4793134FEED.body
}

void ConfigMgr::merge (const ConfigMgr& other, bool override)
{
  //## begin ConfigMgr::merge%78C52656FEED.body preserve=yes
  int nused=0;
  for( CCMI iter = other.config_.begin(); iter != other.config_.end(); iter++ )
    if( override || config_.find(iter->first) == config_.end() )
    {
      nused++;
      config_.insert(*iter);
    }
  dprintf(3)("%d/%d config_ entries merged in\n",other.size(),nused);
  //## end ConfigMgr::merge%78C52656FEED.body
}

void ConfigMgr::merge (int argc, const char** argv, bool override)
{
  //## begin ConfigMgr::merge%C8B74B35FEED.body preserve=yes
  int nread=0,nused=0;
  for( int i=0; i<argc; i++ )
  {
    int res = mergeLine(argv[i],override);
    nread += (res>=0);
    nused += (res>0);
  }  
  dprintf(3)("%d/%d config_ entries merged in\n",nread,nused);
  //## end ConfigMgr::merge%C8B74B35FEED.body
}

void ConfigMgr::merge (const vector<string> &str, bool override)
{
  //## begin ConfigMgr::merge%7D44D79AFEED.body preserve=yes
  int nread=0,nused=0;
  for( vector<string>::const_iterator iter = str.begin(); iter != str.end(); iter++ )
  {
    int res = mergeLine(*iter,override);
    nread += (res>=0);
    nused += (res>0);
  }  
  dprintf(3)("%d/%d config_ entries merged in\n",nread,nused);
  //## end ConfigMgr::merge%7D44D79AFEED.body
}

int ConfigMgr::mergeLine (const string& str, bool override)
{
  //## begin ConfigMgr::mergeLine%DC7A9961FEED.body preserve=yes
  if( str[0] == '-' )
    return -1;
  size_t pos = str.find_first_of('=');
  if( pos == string::npos )
    return -1;
  string name = str.substr(0,pos),
         value = str.substr(pos+1);
  if( override || config_.find(name) == config_.end() )
  {
    config_[name] = value;
    return 1;
  }
  else
    return 0;
  //## end ConfigMgr::mergeLine%DC7A9961FEED.body
}

bool ConfigMgr::get (const string& name, int& value) const
{
  //## begin ConfigMgr::get%F23874E0FEED.body preserve=yes
  string val;
  if( !get(name,val) )
    return False;
  value = atoi(val.c_str());
  return True;
  //## end ConfigMgr::get%F23874E0FEED.body
}

bool ConfigMgr::get (const string& name, string& value) const
{
  //## begin ConfigMgr::get%DF69BB1FFEED.body preserve=yes
  CCMI iter = config_.find(name);
  if( iter != config_.end() )
  {
    value = iter->second;
    return True;
  }
  return False;
  //## end ConfigMgr::get%DF69BB1FFEED.body
}

void ConfigMgr::set (const string& name, int value)
{
  //## begin ConfigMgr::set%593209CEFEED.body preserve=yes
  char s[32];
  sprintf(s,"%d",value);
  set(name,s);
  //## end ConfigMgr::set%593209CEFEED.body
}

void ConfigMgr::set (const string& name, string value)
{
  //## begin ConfigMgr::set%D175196EFEED.body preserve=yes
  config_[name] = value;
  //## end ConfigMgr::set%D175196EFEED.body
}

bool ConfigMgr::remove (const string& name)
{
  //## begin ConfigMgr::remove%6A93DD0EFEED.body preserve=yes
  CMI iter = config_.find(name);
  if( iter != config_.end() )
  {
    config_.erase(iter);
    return True;
  }
  return False;
  //## end ConfigMgr::remove%6A93DD0EFEED.body
}

// Additional Declarations
  //## begin ConfigMgr%3CCFFDC300DA.declarations preserve=yes
  //## end ConfigMgr%3CCFFDC300DA.declarations

//## begin module%3CCFFF3301FC.epilog preserve=yes
//## end module%3CCFFF3301FC.epilog
