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

#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include "OctopussyConfig.h"

namespace Octopussy
{

OctopussyConfig 
    OctopussyConfig::global_( getenv("HOME") + string("/.octopussy") );


// Class OctopussyConfig 

OctopussyConfig::OctopussyConfig (const string &confdir)
    : configdir(confdir)
{
}



void OctopussyConfig::init (int argc, const char **argv)
{
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
  merge(configdir + globalfile,true,true);
  merge(configdir + hostfile,true,true);
  if( progfile.length() )
    merge(configdir + progfile,true,true);
  // merge in (and override) with local config files, if any
  merge(globalfile,true,true);
  merge(hostfile,true,true);
  if( progfile.length() )
    merge( progfile,true,true);
  // merge in local file, if specified
  if( localfile.length() )
    merge( localfile,true,true);
  // finally, merge in command line
  merge(args_,true);
  
  dprintf(1)("%d entries configured\n",config().size());
  if( Debug(3) )
  {
    for( CCMI iter = config().begin(); iter != config().end(); iter++ )
      dprintf(3)("entry %s=%s\n",iter->first.c_str(),iter->second.c_str());
  }
}

bool OctopussyConfig::getOption (const string &name) const
{
  string dum;
  return getOption(name,dum);
}

bool OctopussyConfig::getOption (const string &name, int &value) const
{
  string val;
  if( !getOption(name,val) )
    return false;
  value = atoi(val.c_str());
  return true;
}

bool OctopussyConfig::getOption (string name, string &value) const
{
  if( name[0] != '-' )
    name = '-' + name;
  
  for( int i=1; i < argc(); i++ )
  {
    if( !argv(i).compare(0,name.length(),name) )
    {
      // specified as "-ovalue"
      if( argv(i).length() > name.length() )
        value = argv(i).substr(name.length());
      // specified as "-o value"
      else if( i < argc()-1 )
        value = argv(i+1);
      else
        value = "";
      return true;
    }
  }
  return false;
}

};
