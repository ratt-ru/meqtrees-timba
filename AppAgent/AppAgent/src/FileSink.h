#ifndef APPAGENT_SRC_FILESINK_H_HEADER_INCLUDED_CA2F6569
#define APPAGENT_SRC_FILESINK_H_HEADER_INCLUDED_CA2F6569

#include <DMI/BlockableObject.h>
#include <DMI/HIID.h>
#include <AppAgent/AppEventSink.h>
#include <AppAgent/AID-AppAgent.h>    
    
#include <deque>

#pragma aid Header Data Footer
    
namespace AppState
{
//##ModelId=3EC9F6EB02F7
  typedef enum
  {
    HEADER = -AidHeader_int,
    FOOTER = -AidFooter_int,
    DATA   = -AidData_int
  }
  AppState_FileSink;
};
        
//##ModelId=3EB9163E00AF
class FileSink : public AppEventSink
{
  public:
    //##ModelId=3EB9169701B4
    //##Documentation
    //## gets event from file
    virtual int getEvent (HIID &id, ObjRef &data, const HIID &mask, int wait = AppEvent::WAIT, HIID &source = _dummy_hiid);

    //##ModelId=3EB916A5000E
    //##Documentation
    //## checks for event in file
    virtual int hasEvent (const HIID &mask, HIID &out) const;

    //##ModelId=3EC243E800C7
    //##Documentation
    //## Returns agent state
    virtual int state() const;

    //##ModelId=3EC243E8023F
    //##Documentation
    //## Returns agent state as a string
    virtual string stateString() const;

  protected:
    //##ModelId=3EB916630067
    FileSink();

    //##ModelId=3EB92AEF01C3
    //##Documentation
    //## called to put more objects on the stream. Returns SUCCESS if something
    //## was put on, or <0 code (ERROR/CLOSED/whatever)
    virtual int refillStream () =0;
    
    //##ModelId=3EB92AEE0279
    void putOnStream (const HIID &id,const ObjRef::Xfer &ref);
    
    //##ModelId=3EC2461201A1
    int setState (int newstate);
    
    //##ModelId=3EC2461203CD
    int setErrorState (const string &error = "" );
    
  private:
    //##ModelId=3EB91663019B
    FileSink(const FileSink& right);
    //##ModelId=3EB916630210
    FileSink& operator=(const FileSink& right);
    
    
    //##ModelId=3EC2434403DC
    typedef struct { HIID id; ObjRef ref; } StreamEntry;
    
    //##ModelId=3EC24345039F
    std::deque<StreamEntry> input_stream_;
    
    //##ModelId=3EC243460187
    int state_;
    //##ModelId=3EC24346021D
    string error_string_;
};

inline int FileSink::state() const
{
  return state_;
}

#endif /* APPAGENT_SRC_FILESINK_H_HEADER_INCLUDED_CA2F6569 */
