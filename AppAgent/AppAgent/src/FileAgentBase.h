#ifndef VISAGENT_SRC_FILEAGENTBASE_H_HEADER_INCLUDED_E39B3406
#define VISAGENT_SRC_FILEAGENTBASE_H_HEADER_INCLUDED_E39B3406

#include <string>
    
namespace AppAgent
{    

using std::string;

namespace AppState
{
//##ModelId=3E8C1A5B00B0
  typedef enum 
  {
    CLOSED    =     -100
  } FileAgentStates;
  
};
    
namespace VisAgent 
{

//##ModelId=3E282C030062
class FileAgentBase
{
  protected:
    //##ModelId=3DF9FECD015F
    typedef enum {
        FILECLOSED  = 0,
        HEADER      = 1,
        DATA        = 2,
        ENDFILE     = 3,
        FILEERROR   = 4
      } FileState;
        
    //##ModelId=3E282C9703C9
    FileAgentBase();
        
    //##ModelId=3DF9FECE012A
    FileState fileState() const;
        
    //##ModelId=3DF9FECE0154
    void setFileState (FileState state);

    //##ModelId=3DF9FECE01CA
    void setErrorState (const string &msg);

    //##ModelId=3DFDFC07004C
    string fileStateString () const;
    
    //##ModelId=3E282AE200E0
    string errorString () const;

  private:
    //##ModelId=3E2818F200A5
    string errmsg_;

    //##ModelId=3E282CE80245
    FileState state_;

};

//##ModelId=3E282C9703C9
inline FileAgentBase::FileAgentBase ()
    : state_(FILECLOSED)
{}

//##ModelId=3DF9FECE012A
inline FileAgentBase::FileState FileAgentBase::fileState() const
{ return state_; }

//##ModelId=3DF9FECE0154
inline void FileAgentBase::setFileState(FileState state)
{ state_ = state; }

//##ModelId=3E282AE200E0
inline string FileAgentBase::errorString() const
{ return errmsg_; }


} // namespace VisAgent

};
#endif /* VISAGENT_SRC_VISFILEAGENTBASE_H_HEADER_INCLUDED_E39B3406 */
