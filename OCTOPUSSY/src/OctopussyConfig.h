#ifndef OctopussyConfig_h
#define OctopussyConfig_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"

#include <vector>
#include <string>

// ConfigMgr
#include "DMI/ConfigMgr.h"

//##ModelId=3CD00368038B
class OctopussyConfig : public ConfigMgr
{
  public:
      //##ModelId=3CD005FD01DC
      OctopussyConfig (const string &confdir);


      //##ModelId=3CD0060C00A7
      void init (int argc, const char **argv);

      //##ModelId=3CD008910330
      int argc () const;

      //##ModelId=3CD00896034B
      const string & argv (int i) const;

      //##ModelId=3CD0061B0258
      bool getOption (const string &name) const;

      //##ModelId=3CD0063503BD
      bool getOption (const string &name, int &value) const;

      //##ModelId=3CD006460137
      bool getOption (string name, string &value) const;

      //##ModelId=3CD0064F01D0
      static void initGlobal (int argc, const char **argv);

    //##ModelId=3DB936CB00F6
      const string& appName () const;

    //##ModelId=3DB936CB0178
      const string& appPath () const;

    //##ModelId=3DB936CB01E7
      const string& hostname () const;

    //##ModelId=3DB936CB0273
      const string& fullHostname () const;

    //##ModelId=3DB936CB02EB
      const vector<string>& args () const;

    // Additional Public Declarations
    //##ModelId=3DB936CB0377
      static const OctopussyConfig & global();
      
    //##ModelId=3DB936CC001B
      string sdebug (int=0) const;
    //##ModelId=3DB936CC015C
      const char *debug (int=0) const   { return sdebug().c_str(); }
  private:
    // Data Members for Class Attributes

      //##ModelId=3CD0059E0009
      string configdir;

      //##ModelId=3CD005CA01C5
      string appName_;

      //##ModelId=3CD005D2037F
      string appPath_;

      //##ModelId=3CD005DB00A7
      string hostname_;

      //##ModelId=3CD005E2027E
      string fullHostname_;

      //##ModelId=3CD005ED031A
      vector<string> args_;

    // Additional Implementation Declarations
    //##ModelId=3DB936CB00A9
      static OctopussyConfig global_;
};

// Class OctopussyConfig 


//##ModelId=3CD008910330
inline int OctopussyConfig::argc () const
{
  return args_.size();
}

//##ModelId=3CD00896034B
inline const string & OctopussyConfig::argv (int i) const
{
  return args_[i];
}

//##ModelId=3CD0064F01D0
inline void OctopussyConfig::initGlobal (int argc, const char **argv)
{
  global_.init(argc,argv);
}

//##ModelId=3DB936CB00F6
inline const string& OctopussyConfig::appName () const
{
  return appName_;
}

//##ModelId=3DB936CB0178
inline const string& OctopussyConfig::appPath () const
{
  return appPath_;
}

//##ModelId=3DB936CB01E7
inline const string& OctopussyConfig::hostname () const
{
  return hostname_;
}

//##ModelId=3DB936CB0273
inline const string& OctopussyConfig::fullHostname () const
{
  return fullHostname_;
}

//##ModelId=3DB936CB02EB
inline const vector<string>& OctopussyConfig::args () const
{
  return args_;
}

//##ModelId=3DB936CB0377
inline const OctopussyConfig & OctopussyConfig::global()
{
  return global_;
}

//##ModelId=3DB936CC001B
inline string OctopussyConfig::sdebug (int) const
{
  return "Config("+hostname_+","+appName_+")";
}


#endif
