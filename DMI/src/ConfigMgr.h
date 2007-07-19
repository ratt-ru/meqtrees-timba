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

#ifndef DMI_ConfigMgr_h
#define DMI_ConfigMgr_h 1

#include <DMI/DMI.h>
#include <TimBase/Debug.h>
    
namespace DMI
{

//##ModelId=3CCFFDC300DA
class ConfigMgr 
{
  public:
      //##ModelId=EA0590B8FEED
      ConfigMgr (const string& fname = "", bool nothrow = false);


      //##ModelId=0778FED4FEED
      int size () const;

      //##ModelId=6B6C3E18FEED
      void clear ();

      //##ModelId=C0C4E648FEED
      void load (const string& fname, bool nothrow = false);

      //##ModelId=80D7E19EFEED
      bool save (string fname = "", bool nothrow = false);

      //##ModelId=B4793134FEED
      bool merge (const string& fname, bool override = true, bool nothrow = false);

      //##ModelId=78C52656FEED
      void merge (const ConfigMgr& other, bool override = true);

      //##ModelId=C8B74B35FEED
      void merge (int argc, const char** argv, bool override = true);

      //##ModelId=7D44D79AFEED
      void merge (const vector<string> &str, bool override = true);

      //##ModelId=DC7A9961FEED
      int mergeLine (const string& str, bool override = true);

      //##ModelId=F23874E0FEED
      bool get (const string& name, int& value) const;

      //##ModelId=DF69BB1FFEED
      bool get (const string& name, string& value) const;

      //##ModelId=90F75FACFEED
      void get (const string& name, int& value, int deflt) const;

      //##ModelId=06281C53FEED
      void get (const string& name, string& value, const string& deflt) const;

      //##ModelId=593209CEFEED
      void set (const string& name, int value);

      //##ModelId=D175196EFEED
      void set (const string& name, string value);

      //##ModelId=6A93DD0EFEED
      bool remove (const string& name);

    // Additional Public Declarations
    //##ModelId=3DB9344E0303
      string sdebug (int=0) const       { return "ConfigMgr"; }
    //##ModelId=3DB9344F0224
      const char *debug (int=0) const   { return sdebug().c_str(); }
      
    //##ModelId=3DB9344D030C
      LocalDebugSubContext;
      
  protected:
    // Additional Protected Declarations
    //##ModelId=3DB9343A027B
      typedef map<string,string> ConfigMap;
    //##ModelId=3DB9343A0307
      typedef ConfigMap::iterator CMI;
    //##ModelId=3DB9343A0393
      typedef ConfigMap::const_iterator CCMI;
      
    //##ModelId=3DB934500058
      ConfigMap & config ();
  private:
    // Additional Implementation Declarations
    //##ModelId=3DB9344E0097
      ConfigMap config_;
    //##ModelId=3DB9344E0141
      string filename;      
};

// Class ConfigMgr 


//##ModelId=90F75FACFEED
inline void ConfigMgr::get (const string& name, int& value, int deflt) const
{
  if( !get(name,value) )
    value = deflt;
}

//##ModelId=06281C53FEED
inline void ConfigMgr::get (const string& name, string& value, const string& deflt) const
{
  if( !get(name,value) )
    value = deflt;
}

//##ModelId=3DB934500058
inline ConfigMgr::ConfigMap & ConfigMgr::config () 
{ 
  return config_; 
}

};
#endif
