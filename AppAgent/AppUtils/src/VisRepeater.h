#ifndef APPUTILS_VISREPEATER_H_HEADER_INCLUDED_BB5EBE76
#define APPUTILS_VISREPEATER_H_HEADER_INCLUDED_BB5EBE76
    
#include <Common/Thread.h>
#include <Common/Thread/Mutex.h>
#include <AppUtils/VisPipe.h>

#pragma aidgroup AppUtils
#pragma aid VisRepeater Repeater
    
namespace VisRepeaterVocabulary
{
  using namespace ApplicationVocabulary;
  
  // define additional control states
//##ModelId=3E8C1A5B01F0
  typedef enum 
  {
      OUTPUT_ERROR  = 1024,     // error on output stream, still running
      INPUT_CLOSED  = -1024,    // input stream has been closed
      INPUT_ERROR   = -1025     // error on input stream
          
  } AppStates;
    
};
        
//##ModelId=3E39285A0273
class VisRepeater : public VisPipe
{
  public:
    //##ModelId=3E392B78035E
    VisRepeater()
    {}
  
    //##ModelId=3E392C570286
    virtual void run ();
    
    //##ModelId=3E392EE403C8
    virtual string stateString() const;
    
    //##ModelId=3E3FEB5002A5
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E3FEDB80357
    LocalDebugSubContext;
    
  private:
    //##ModelId=3E77397D034C
    VisRepeater(const VisRepeater& right);
    //##ModelId=3E392B78038F
    VisRepeater& operator=(const VisRepeater& right);
};

#endif /* DATAREPEATER_H_HEADER_INCLUDED_BB5EBE76 */
