//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3CCFFF3301E8.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3CCFFF3301E8.cm

//## begin module%3CCFFF3301E8.cp preserve=no
//## end module%3CCFFF3301E8.cp

//## Module: ConfigMgr%3CCFFF3301E8; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\dmi\src\ConfigMgr.h

#ifndef ConfigMgr_h
#define ConfigMgr_h 1

//## begin module%3CCFFF3301E8.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
//## end module%3CCFFF3301E8.additionalIncludes

//## begin module%3CCFFF3301E8.includes preserve=yes
#include "Common/Debug.h"
//## end module%3CCFFF3301E8.includes

//## begin module%3CCFFF3301E8.declarations preserve=no
//## end module%3CCFFF3301E8.declarations

//## begin module%3CCFFF3301E8.additionalDeclarations preserve=yes
//## end module%3CCFFF3301E8.additionalDeclarations


//## begin ConfigMgr%3CCFFDC300DA.preface preserve=yes
//## end ConfigMgr%3CCFFDC300DA.preface

//## Class: ConfigMgr%3CCFFDC300DA
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



class ConfigMgr 
{
  //## begin ConfigMgr%3CCFFDC300DA.initialDeclarations preserve=yes
  LocalDebugSubContext;
  //## end ConfigMgr%3CCFFDC300DA.initialDeclarations

  public:
    //## Constructors (specified)
      //## Operation: ConfigMgr%EA0590B8FEED; C++
      ConfigMgr (const string& fname = "", bool nothrow = False);


    //## Other Operations (specified)
      //## Operation: size%0778FED4FEED; C++
      int size () const;

      //## Operation: clear%6B6C3E18FEED; C++
      void clear ();

      //## Operation: load%C0C4E648FEED; C++
      void load (const string& fname, bool nothrow = False);

      //## Operation: save%80D7E19EFEED; C++
      bool save (string fname = "", bool nothrow = False);

      //## Operation: merge%B4793134FEED; C++
      bool merge (const string& fname, bool override = True, bool nothrow = False);

      //## Operation: merge%78C52656FEED; C++
      void merge (const ConfigMgr& other, bool override = True);

      //## Operation: merge%C8B74B35FEED; C++
      void merge (int argc, const char** argv, bool override = True);

      //## Operation: merge%7D44D79AFEED; C++
      void merge (const vector<string> &str, bool override = True);

      //## Operation: mergeLine%DC7A9961FEED; C++
      int mergeLine (const string& str, bool override = True);

      //## Operation: get%F23874E0FEED; C++
      bool get (const string& name, int& value) const;

      //## Operation: get%DF69BB1FFEED; C++
      bool get (const string& name, string& value) const;

      //## Operation: get%90F75FACFEED; C++
      void get (const string& name, int& value, int deflt) const;

      //## Operation: get%06281C53FEED; C++
      void get (const string& name, string& value, const string& deflt) const;

      //## Operation: set%593209CEFEED; C++
      void set (const string& name, int value);

      //## Operation: set%D175196EFEED; C++
      void set (const string& name, string value);

      //## Operation: remove%6A93DD0EFEED; C++
      bool remove (const string& name);

    // Additional Public Declarations
      //## begin ConfigMgr%3CCFFDC300DA.public preserve=yes
      string sdebug (int=0) const       { return "ConfigMgr"; }
      const char *debug (int=0) const   { return sdebug().c_str(); }
      //## end ConfigMgr%3CCFFDC300DA.public
  protected:
    // Additional Protected Declarations
      //## begin ConfigMgr%3CCFFDC300DA.protected preserve=yes
      typedef map<string,string> ConfigMap;
      typedef ConfigMap::iterator CMI;
      typedef ConfigMap::const_iterator CCMI;
      
      ConfigMap & config ();
      //## end ConfigMgr%3CCFFDC300DA.protected
  private:
    // Additional Private Declarations
      //## begin ConfigMgr%3CCFFDC300DA.private preserve=yes
      //## end ConfigMgr%3CCFFDC300DA.private

  private: //## implementation
    // Additional Implementation Declarations
      //## begin ConfigMgr%3CCFFDC300DA.implementation preserve=yes
      ConfigMap config_;
      string filename;      
      //## end ConfigMgr%3CCFFDC300DA.implementation
};

//## begin ConfigMgr%3CCFFDC300DA.postscript preserve=yes
//## end ConfigMgr%3CCFFDC300DA.postscript

// Class ConfigMgr 


//## Other Operations (inline)
inline void ConfigMgr::get (const string& name, int& value, int deflt) const
{
  //## begin ConfigMgr::get%90F75FACFEED.body preserve=yes
  if( !get(name,value) )
    value = deflt;
  //## end ConfigMgr::get%90F75FACFEED.body
}

inline void ConfigMgr::get (const string& name, string& value, const string& deflt) const
{
  //## begin ConfigMgr::get%06281C53FEED.body preserve=yes
  if( !get(name,value) )
    value = deflt;
  //## end ConfigMgr::get%06281C53FEED.body
}

//## begin module%3CCFFF3301E8.epilog preserve=yes
inline ConfigMgr::ConfigMap & ConfigMgr::config () 
{ 
  return config_; 
}
//## end module%3CCFFF3301E8.epilog


#endif
