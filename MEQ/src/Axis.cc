#include <DMI/Record.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/Axis.h>
#include <MEQ/Meq.h>

namespace Meq {
  
using namespace DebugMeq;

namespace Axis {
  
int FREQ = 0;
int TIME = 1;

// mappings between names and numbers
HIID _name_map[MaxAxis];
std::map<HIID,int> _num_map;
bool _default_mapping = true;

// vector containing description records
static DMI::Vec::Ref axis_recs,axis_ids;

// Defines name of axis i 
// * if the name is just "i", does nothing 
// * if a name for the axis is already defined, it must be the same,
//   throws exception otherwise
// * else adds name for the axis
static void defineAxis (int i,const HIID &name,bool addrec=true)
{
  _init();
  // name_index will be the axis number if name is just "n", else -1
  int name_index;
  if( name.size() == 1 )
    name_index = name[0].index();
  else
    name_index = -1;
  // if name is a number, check that it matches i, if so, do nothing,
  // else throw error (i.e. we can't name axis 1 to be "2")(
  if( name_index >= 0 )
  {
    FailWhen(name_index != i,
             Debug::ssprintf("can't define axis %d as '%d'",i,name_index));
    return;
  }
  // if axis is already has a name, check for match
  if( _name_map[i] != AtomicID(i) )
  { 
    // unspecified axes have the name "i", so this name we can always override 
    FailWhen(_name_map[i] != name,
             Debug::ssprintf("can't define axis %d as '%s': already defined as '%s'",
                i,_name_map[i].toString().c_str(),name.toString().c_str()));
    return;
  }
  // now define the axis
  _name_map[i] = axis_ids[i] = name;
  _num_map[name] = i;
  if( name == HIID(AidFreq) )
    FREQ = i;
  else if( name == HIID(AidTime) )
    TIME = i;
  // init record for axis
  if( addrec )
  {
    DMI::Record & axrec = axis_recs[i].replace() <<= new DMI::Record;
    axrec[AidId] = name;
  }
  axis_ids[i] = name;
}

template<class Iter>
static void setAxisMap (Iter begin,Iter end)
{
  _init();
  int i=0;
  for( ; begin<end; i++,begin++ )
  {
    FailWhen(i >= MaxAxis,"too many axes in mapping");
    defineAxis(i,*begin);
  }
  // fill the rest with numbers
  for( ; i<MaxAxis; i++ )
  {
    defineAxis(i,AtomicID(i));
  }
  // mapping no longer default
  _default_mapping = false;
}

void setAxisMap (const DMI::Vec &map)
{
  _init();
  FailWhen(map.type() != TpDMIHIID,"axis map: expected HIIDs, got "+map.type().toString());
  FailWhen(map.size() > MaxAxis,"too many axes in mapping");
  for( int i=0; i<map.size(); i++ )
    defineAxis(i,map[i].as<HIID>());
  _default_mapping = false;
}

void setAxisMap (const std::vector<HIID> &map)
{
  setAxisMap(map.begin(),map.end());
}

void setAxisMap (const HIID names[],int num)
{
  setAxisMap(names,names+num);
}

const DMI::Vec & getAxisRecords ()
{
  _init();
  return *axis_recs;
}

const DMI::Vec & getAxisIds ()
{
  _init();
  return *axis_ids;
}

void setAxisRecords (const DMI::Vec & vec)
{
  _init();
  FailWhen(vec.type() != TpDMIRecord,"expected vector of axis records");
  FailWhen(vec.size() > MaxAxis,"too many axis records specified");
  int i=0;
  for( ; i<vec.size(); i++ )
  {
    DMI::Record::Ref rec = vec[i].ref();
    HIID name = AtomicID(i);
    bool addrec = false;
    // get name
    rec()[AidId].get(name,true);
    // add to map
    defineAxis(i,name);
    // replace axis record 
    axis_recs[i].replace() <<= rec;
  }
  _default_mapping = false;
}

void addAxis (const HIID &name)
{
  _init();
  // return axis if found
  int n = axis(name,true);
  if( n >= 0 )
    return;
  // allocate new
  for( int i=0; i<MaxAxis; i++ )
    if( _name_map[i] == AtomicID(i) )
    {
      defineAxis(i,name);
      // mapping no longer default
      _default_mapping = false;
      return;
    }
  // out of axes
  Throw("too many axes defined");
}

// init default map of TIME/FREQ
void resetDefaultMap ()
{
  axis_recs <<= new DMI::Vec(TpDMIRecord,MaxAxis);
  axis_ids  <<= new DMI::Vec(TpDMIHIID,MaxAxis);
  
  // clear existing definitions
  _num_map.clear();
  for( int i=0; i<MaxAxis; i++ )
    _name_map[i] = AtomicID(i);
  const HIID defmap[] = { AidTime,AidFreq };
  setAxisMap(defmap,sizeof(defmap)/sizeof(defmap[0]));
  // reset default_mapping flag again since it was cleared by setAxisMap()
  _default_mapping = true;
}

}}; // close both namespaces
  
