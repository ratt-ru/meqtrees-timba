//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <time.h>

#include "ConfigMgr.h"

namespace DMI
{

InitDebugSubContext(ConfigMgr,DebugDMI,"Config");


ConfigMgr::ConfigMgr (const string& fname, bool nothrow)
{
  if( fname.length() )
    load(fname,nothrow);
}



//##ModelId=0778FED4FEED
//## Other Operations (implementation)
int ConfigMgr::size () const
{
  return config_.size();
}

//##ModelId=6B6C3E18FEED
void ConfigMgr::clear ()
{
  config_.clear();
}

//##ModelId=C0C4E648FEED
void ConfigMgr::load (const string& fname, bool nothrow)
{
  clear();
  merge(filename=fname,true,nothrow);
}

//##ModelId=80D7E19EFEED
bool ConfigMgr::save (string fname, bool nothrow)
{
  // empty file means use current filename
  if( !fname.length() )
  {
    fname = filename;
    if( !fname.length() )
      if( nothrow )
        return false;
      else
        Throw("ConfigMgr::save(): null filename");
  }
  FILE *f = fopen(fname.c_str(),"wt");
  if( !f )
    if( nothrow )
      return false;
    else
      Throw("open("+fname+"): "+strerror(errno));
  time_t tm = time(0);
  fprintf(f,"# configuration saved on %s\n",ctime(&tm));
  for( CCMI iter = config_.begin(); iter != config_.end(); iter++ )
    fprintf(f,"%s %s\n",iter->first.c_str(),iter->second.c_str());
  fclose(f);
  dprintf(2)("%d config_ entries saved to %s\n",config_.size(),fname.c_str());
  return true;
}

//##ModelId=B4793134FEED
bool ConfigMgr::merge (const string& fname, bool override, bool nothrow)
{
  FILE *f = fopen(fname.c_str(),"rt");
  if( !f )
  {
    if( nothrow )
    {
      dprintf(2)("merge: can't open file %s (%s)\n",fname.c_str(),strerror(errno));
      return false;
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
  return true;
}

//##ModelId=78C52656FEED
void ConfigMgr::merge (const ConfigMgr& other, bool override)
{
  int nused=0;
  for( CCMI iter = other.config_.begin(); iter != other.config_.end(); iter++ )
    if( override || config_.find(iter->first) == config_.end() )
    {
      nused++;
      config_.insert(*iter);
    }
  dprintf(3)("%d/%d config_ entries merged in\n",other.size(),nused);
}

//##ModelId=C8B74B35FEED
void ConfigMgr::merge (int argc, const char** argv, bool override)
{
  int nread=0,nused=0;
  for( int i=0; i<argc; i++ )
  {
    int res = mergeLine(argv[i],override);
    nread += (res>=0);
    nused += (res>0);
  }  
  dprintf(3)("%d/%d config_ entries merged in\n",nread,nused);
}

//##ModelId=7D44D79AFEED
void ConfigMgr::merge (const vector<string> &str, bool override)
{
  int nread=0,nused=0;
  for( vector<string>::const_iterator iter = str.begin(); iter != str.end(); iter++ )
  {
    int res = mergeLine(*iter,override);
    nread += (res>=0);
    nused += (res>0);
  }  
  dprintf(3)("%d/%d config_ entries merged in\n",nread,nused);
}

//##ModelId=DC7A9961FEED
int ConfigMgr::mergeLine (const string& str, bool override)
{
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
}

//##ModelId=F23874E0FEED
bool ConfigMgr::get (const string& name, int& value) const
{
  string val;
  if( !get(name,val) )
    return false;
  value = atoi(val.c_str());
  return true;
}

//##ModelId=DF69BB1FFEED
bool ConfigMgr::get (const string& name, string& value) const
{
  CCMI iter = config_.find(name);
  if( iter != config_.end() )
  {
    value = iter->second;
    return true;
  }
  return false;
}

//##ModelId=593209CEFEED
void ConfigMgr::set (const string& name, int value)
{
  char s[32];
  sprintf(s,"%d",value);
  set(name,s);
}

//##ModelId=D175196EFEED
void ConfigMgr::set (const string& name, string value)
{
  config_[name] = value;
}

//##ModelId=6A93DD0EFEED
bool ConfigMgr::remove (const string& name)
{
  CMI iter = config_.find(name);
  if( iter != config_.end() )
  {
    config_.erase(iter);
    return true;
  }
  return false;
}


}
