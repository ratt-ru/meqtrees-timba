#ifndef APPUTILS_SRC_VISPIPE_H_HEADER_INCLUDED_FF9DF2AD
#define APPUTILS_SRC_VISPIPE_H_HEADER_INCLUDED_FF9DF2AD
    
#include <AppUtils/ApplicationBase.h>
#include <VisAgent/InputAgent.h>
#include <VisAgent/OutputAgent.h>

//##ModelId=3E7727920352
class VisPipe : public ApplicationBase
{
  private:
    //##ModelId=3E7728510172
    VisAgent::InputAgent * input_;
    //##ModelId=3E7728640039
    VisAgent::OutputAgent * output_;

  public:
    //##ModelId=3E7725FA03DE
    virtual void attach(VisAgent::InputAgent *inp, int flags);
    //##ModelId=3E7725FB0002
    virtual void attach(VisAgent::OutputAgent *outp, int flags);
    
    //##ModelId=3E78955E0197
    virtual bool verifySetup(bool throw_exc = False) const;

    //##ModelId=3E43BC04002F
    VisAgent::InputAgent &input()
    { return *input_; }
    //##ModelId=3E43BC040043
    VisAgent::OutputAgent & output()
    { return *output_; }
    //##ModelId=3E772B090393
    const VisAgent::InputAgent & input() const
    { return *input_; }
    //##ModelId=3E772B0A0210
    const VisAgent::OutputAgent & output() const 
    { return *output_; }
    //##ModelId=3E78948C0114
    bool hasInputAgent () const       { return input_ != 0;  }
    //##ModelId=3E78948C031C
    bool hasOutputAgent () const      { return output_ != 0; }

  protected:
    //##ModelId=3E7728010327
    VisPipe ();

  private:
    //##ModelId=3E77282D022D
    VisPipe (const VisPipe& right);
    //##ModelId=3E77282E0090
    VisPipe& operator=(const VisPipe& right);


};



#endif /* APPUTILS_SRC_VISPIPE_H_HEADER_INCLUDED_FF9DF2AD */
