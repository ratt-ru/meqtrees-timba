#ifndef APPREGISTRY_H_HEADER_INCLUDED_ACE7E2A7
#define APPREGISTRY_H_HEADER_INCLUDED_ACE7E2A7

#include <DMI/DataRecord.h>
#include <OCTOPUSSY/WPInterface.h>

//##ModelId=3E3012F500C7
class AppRegistry
{
  public:
    //##ModelId=3E3013BC00F4
    typedef WPRef (*Constructor)(DataRecord::Ref &initrecord);

  
    //##ModelId=3E3013C2008F
    static void registerApp (AtomicID id,Constructor ctor);

  
    //##ModelId=3E30141D00CA
    static bool isRegistered (AtomicID id);

  
    //##ModelId=3E30143C0391
    static int construct (WPRef &out,AtomicID id,DataRecord::Ref &initrec);

  private:
    //##ModelId=3E3013BC0112
    DeclareRegistry(AppRegistry,AtomicID,Constructor);
};



#endif /* APPREGISTRY_H_HEADER_INCLUDED_ACE7E2A7 */
