//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CD0078A01DD.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CD0078A01DD.cm

//## begin module%3CD0078A01DD.cp preserve=no
//## end module%3CD0078A01DD.cp

//## Module: OctopussyConfig%3CD0078A01DD; Package specification
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\OctopussyConfig.h

#ifndef OctopussyConfig_h
#define OctopussyConfig_h 1

//## begin module%3CD0078A01DD.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3CD0078A01DD.additionalIncludes

//## begin module%3CD0078A01DD.includes preserve=yes
#include <vector>
#include <string>
//## end module%3CD0078A01DD.includes

// ConfigMgr
#include "DMI/ConfigMgr.h"
//## begin module%3CD0078A01DD.declarations preserve=no
//## end module%3CD0078A01DD.declarations

//## begin module%3CD0078A01DD.additionalDeclarations preserve=yes
//## end module%3CD0078A01DD.additionalDeclarations


//## begin OctopussyConfig%3CD00368038B.preface preserve=yes
//## end OctopussyConfig%3CD00368038B.preface

//## Class: OctopussyConfig%3CD00368038B
//## Category: OCTOPUSSY%3BCEC935032A
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class OctopussyConfig : public ConfigMgr  //## Inherits: <unnamed>%3CD0077A0021
{
  //## begin OctopussyConfig%3CD00368038B.initialDeclarations preserve=yes
  //## end OctopussyConfig%3CD00368038B.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: OctopussyConfig%3CD005FD01DC
      OctopussyConfig (const string &confdir);


    //## Other Operations (specified)
      //## Operation: init%3CD0060C00A7
      void init (int argc, const char **argv);

      //## Operation: argc%3CD008910330
      int argc () const;

      //## Operation: argv%3CD00896034B
      const string & argv (int i) const;

      //## Operation: getOption%3CD0061B0258
      bool getOption (const string &name) const;

      //## Operation: getOption%3CD0063503BD
      bool getOption (const string &name, int &value) const;

      //## Operation: getOption%3CD006460137
      bool getOption (string name, string &value) const;

      //## Operation: initGlobal%3CD0064F01D0
      static void initGlobal (int argc, const char **argv);

    //## Get and Set Operations for Class Attributes (generated)

      //## Attribute: appName%3CD005CA01C5
      const string& appName () const;

      //## Attribute: appPath%3CD005D2037F
      const string& appPath () const;

      //## Attribute: hostname%3CD005DB00A7
      const string& hostname () const;

      //## Attribute: fullHostname%3CD005E2027E
      const string& fullHostname () const;

      //## Attribute: args%3CD005ED031A
      const vector<string>& args () const;

    // Additional Public Declarations
      //## begin OctopussyConfig%3CD00368038B.public preserve=yes
      static const OctopussyConfig & global();
      
      string sdebug (int=0) const;
      const char *debug (int=0) const   { return sdebug().c_str(); }
      //## end OctopussyConfig%3CD00368038B.public
  protected:
    // Additional Protected Declarations
      //## begin OctopussyConfig%3CD00368038B.protected preserve=yes
      //## end OctopussyConfig%3CD00368038B.protected

  private:
    // Additional Private Declarations
      //## begin OctopussyConfig%3CD00368038B.private preserve=yes
      //## end OctopussyConfig%3CD00368038B.private

  private: //## implementation
    // Data Members for Class Attributes

      //## Attribute: configdir%3CD0059E0009
      //## begin OctopussyConfig::configdir%3CD0059E0009.attr preserve=no  private: string {U} 
      string configdir;
      //## end OctopussyConfig::configdir%3CD0059E0009.attr

      //## begin OctopussyConfig::appName%3CD005CA01C5.attr preserve=no  public: string {U} 
      string appName_;
      //## end OctopussyConfig::appName%3CD005CA01C5.attr

      //## begin OctopussyConfig::appPath%3CD005D2037F.attr preserve=no  public: string {U} 
      string appPath_;
      //## end OctopussyConfig::appPath%3CD005D2037F.attr

      //## begin OctopussyConfig::hostname%3CD005DB00A7.attr preserve=no  public: string {U} 
      string hostname_;
      //## end OctopussyConfig::hostname%3CD005DB00A7.attr

      //## begin OctopussyConfig::fullHostname%3CD005E2027E.attr preserve=no  public: string {U} 
      string fullHostname_;
      //## end OctopussyConfig::fullHostname%3CD005E2027E.attr

      //## begin OctopussyConfig::args%3CD005ED031A.attr preserve=no  public: vector<string> {U} 
      vector<string> args_;
      //## end OctopussyConfig::args%3CD005ED031A.attr

    // Additional Implementation Declarations
      //## begin OctopussyConfig%3CD00368038B.implementation preserve=yes
      static OctopussyConfig global_;
      //## end OctopussyConfig%3CD00368038B.implementation
};

//## begin OctopussyConfig%3CD00368038B.postscript preserve=yes
//## end OctopussyConfig%3CD00368038B.postscript

// Class OctopussyConfig 


//## Other Operations (inline)
inline int OctopussyConfig::argc () const
{
  //## begin OctopussyConfig::argc%3CD008910330.body preserve=yes
  return args_.size();
  //## end OctopussyConfig::argc%3CD008910330.body
}

inline const string & OctopussyConfig::argv (int i) const
{
  //## begin OctopussyConfig::argv%3CD00896034B.body preserve=yes
  return args_[i];
  //## end OctopussyConfig::argv%3CD00896034B.body
}

inline void OctopussyConfig::initGlobal (int argc, const char **argv)
{
  //## begin OctopussyConfig::initGlobal%3CD0064F01D0.body preserve=yes
  global_.init(argc,argv);
  //## end OctopussyConfig::initGlobal%3CD0064F01D0.body
}

//## Get and Set Operations for Class Attributes (inline)

inline const string& OctopussyConfig::appName () const
{
  //## begin OctopussyConfig::appName%3CD005CA01C5.get preserve=no
  return appName_;
  //## end OctopussyConfig::appName%3CD005CA01C5.get
}

inline const string& OctopussyConfig::appPath () const
{
  //## begin OctopussyConfig::appPath%3CD005D2037F.get preserve=no
  return appPath_;
  //## end OctopussyConfig::appPath%3CD005D2037F.get
}

inline const string& OctopussyConfig::hostname () const
{
  //## begin OctopussyConfig::hostname%3CD005DB00A7.get preserve=no
  return hostname_;
  //## end OctopussyConfig::hostname%3CD005DB00A7.get
}

inline const string& OctopussyConfig::fullHostname () const
{
  //## begin OctopussyConfig::fullHostname%3CD005E2027E.get preserve=no
  return fullHostname_;
  //## end OctopussyConfig::fullHostname%3CD005E2027E.get
}

inline const vector<string>& OctopussyConfig::args () const
{
  //## begin OctopussyConfig::args%3CD005ED031A.get preserve=no
  return args_;
  //## end OctopussyConfig::args%3CD005ED031A.get
}

//## begin module%3CD0078A01DD.epilog preserve=yes
inline const OctopussyConfig & OctopussyConfig::global()
{
  return global_;
}

inline string OctopussyConfig::sdebug (int=0) const
{
  return "Config("+hostname_+","+appName_+")";
}
//## end module%3CD0078A01DD.epilog


#endif
