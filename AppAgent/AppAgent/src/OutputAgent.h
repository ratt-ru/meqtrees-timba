#ifndef VISAGENT_SRC_VISOUTPUTAGENT_H_HEADER_INCLUDED_BB8A6715
#define VISAGENT_SRC_VISOUTPUTAGENT_H_HEADER_INCLUDED_BB8A6715
    
#include <AppAgent/AppAgent.h>
#include <AppAgent/AppEventAgentBase.h>
#include <AppAgent/VisAgentVocabulary.h>
#include <AppAgent/DataStreamMap.h>
#include <VisCube/VTile.h>

namespace AppAgent
{    
using namespace DMI;
class AppEventSink;

namespace VisAgent
{
using namespace VisCube;

//##ModelId=3E00AA5100F9
class OutputAgent : public AppEventAgentBase
{
  public:
    //##ModelId=3E4143600221
    explicit OutputAgent (const HIID &initf = AidOutput);
    //##ModelId=3E41436101A6
    OutputAgent (AppEventSink &sink,const HIID &initf = AidOutput,int flags=0);
    //##ModelId=3E50FAF103A1
    OutputAgent (AppEventSink *sink,const HIID &initf = AidOutput,int flags=0);

    //##ModelId=3EB244510086
    virtual int put (int type,const ObjRef &ref = ObjRef());
    
    //##ModelId=3E28276A0257
    //##Documentation
    //## Puts visibilities header onto output stream. If stream has been
    //## suspended (i.e. from other end), returns WAIT (wait=false), or
    //## blocks until it is resumed (wait=true)
    //## Returns: SUCCESS   on success
    //##          WAIT      stream has been suspended from other end
    //##          CLOSED    stream closed
    int putHeader   (const DMI::Record::Ref &hdr);

    // temporarily
    //##ModelId=3E28276D022A
    //##Documentation
    //## Puts next tile onto output stream. If stream has been
    //## suspended (i.e. from other end), returns WAIT (wait=false), or
    //## blocks until it is resumed (wait=true)
    //## Returns: SUCCESS   on success
    //##          WAIT      stream has been suspended from other end
    //##          OUTOFSEQ  data is out of sequence (must send header first)
    //##          CLOSED    stream closed
    int putNextTile (const VTile::Ref &tile);
    
    //##ModelId=3EB246C2011E
    int putFooter   (const DMI::Record::Ref &ftr);

    //##ModelId=3E41144B0245
    virtual string sdebug (int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=3E9BD640010C
    DefineRefTypes(OutputAgent,Ref);

    
  private:
    //##ModelId=3E4235C203D4
    OutputAgent();
    //##ModelId=3E4235C301A5
    OutputAgent(const OutputAgent& right);
    //##ModelId=3E4235C302E6
    OutputAgent& operator=(const OutputAgent& right);
    
    //##ModelId=3EB246C2003E
    static DataStreamMap & datamap;
};

} // namespace VisAgent
};

#endif /* VISAGENT_SRC_VISOUTPUTAGENT_H_HEADER_INCLUDED_BB8A6715 */

