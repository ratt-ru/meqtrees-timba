#include "MEQ/Node.h"
#include "MEQ/Forest.h"
#include <DMI/BlockSet.h>


namespace MEQ {

//##ModelId=3F5F43E000A0
Node::Node()
{
}

//##ModelId=3F5F44A401BC
Node::~Node()
{
}

//##ModelId=3F5F45D202D5
void Node::init (DataRecord::Ref::Xfer &initrec, Forest* frst)
{
  forest = frst;
  // xfer & privatize the state record -- we don't want anyone
  // changing it under us
  staterec = initrec;
  staterec.privatize(DMI::WRITE|DMI::DEEP);
  // extract node name
  myname = (*staterec)[AidName].as<string>("");
}

//##ModelId=3F5F445A00AC
void Node::setState (const DataRecord &rec)
{
  // copy relevant fields from new record
  // the only relevant one at this level is Name
  if( rec[AidName].exists() )
    staterec()[AidName] = myname = rec[AidName].as<string>();
}

//##ModelId=3F6726C4039D
int Node::getResult (Result::Ref &resref, const Request&)
{
  Throw("MEQ::Node::getResult not implemented");
}

// throw exceptions for unimplemented DMI functions
//##ModelId=3F5F4363030F
CountedRefTarget* Node::clone(int,int) const
{
  Throw("MEQ::Node::clone not implemented");
}

//##ModelId=3F5F43630315
int Node::fromBlock(BlockSet&)
{
  Throw("MEQ::Node::fromBlock not implemented");
}

//##ModelId=3F5F43630318
int Node::toBlock(BlockSet &) const
{
  Throw("MEQ::Node::toBlock not implemented");
}

//##ModelId=3F5F48180303
string Node::sdebug (int detail, const string &prefix, const char *nm) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s(%s)",nm?nm:"MEQ::Node",name().c_str());
  }
  return out;
}

} // namespace MEQ
