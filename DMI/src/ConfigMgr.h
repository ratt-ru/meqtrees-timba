//	f:\lofar\dvl\lofar\cep\cpa\pscf\src

#ifndef ConfigMgr_h
#define ConfigMgr_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include "Common/Debug.h"


//##ModelId=3CCFFDC300DA
class ConfigMgr 
{
    //##ModelId=3DB9344D030C
  LocalDebugSubContext;

  public:
      //##ModelId=EA0590B8FEED
      ConfigMgr (const string& fname = "", bool nothrow = False);


      //##ModelId=0778FED4FEED
      int size () const;

      //##ModelId=6B6C3E18FEED
      void clear ();

      //##ModelId=C0C4E648FEED
      void load (const string& fname, bool nothrow = False);

      //##ModelId=80D7E19EFEED
      bool save (string fname = "", bool nothrow = False);

      //##ModelId=B4793134FEED
      bool merge (const string& fname, bool override = True, bool nothrow = False);

      //##ModelId=78C52656FEED
      void merge (const ConfigMgr& other, bool override = True);

      //##ModelId=C8B74B35FEED
      void merge (int argc, const char** argv, bool override = True);

      //##ModelId=7D44D79AFEED
      void merge (const vector<string> &str, bool override = True);

      //##ModelId=DC7A9961FEED
      int mergeLine (const string& str, bool override = True);

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


#endif
