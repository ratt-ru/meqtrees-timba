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

static void defineAxis (int i,const HIID &name)
{
  FailWhen(!_default_mapping && _name_map[i] != name,
      "different axis mapping already defined");
  _name_map[i] = axis_ids[i] = name;
  _num_map[name] = i;
  if( name == HIID(AidFreq) )
    FREQ = i;
  else if( name == HIID(AidTime) )
    TIME = i;
}

template<class Iter>
static void setAxisMap (Iter begin,Iter end)
{
  int i=0;
  for( ; begin<end; i++,begin++ )
  {
    FailWhen(i >= MaxAxis,"too many axes in mapping");
    defineAxis(i,*begin);
    // init record for axis
    DMI::Record & axrec = axis_recs[i] <<= new DMI::Record;
    axrec[AidId] = *begin;
  }
  // fill the rest with numbers
  for( ; i<MaxAxis; i++ )
  {
    defineAxis(i,AtomicID(i));
    axis_recs().put(i,new DMI::Record);
  }
  // mapping no longer default
  _default_mapping = false;
}

void setAxisMap (const DMI::Vec &map)
{
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
  return *axis_recs;
}

const DMI::Vec & getAxisIds ()
{
  return *axis_ids;
}

void setAxisRecords (const DMI::Vec & vec)
{
  FailWhen(vec.type() != TpDMIRecord,"expected vector of axis records");
  FailWhen(vec.size() > MaxAxis,"too many axis records specified");
  int i=0;
  for( ; i<vec.size(); i++ )
  {
    const DMI::Record &rec = vec[i].as<DMI::Record>();
    HIID name;
    // if no id specified, use axis number
    if( !rec[AidId].get(name) )
      name = AtomicID(i);
    // add to map
    defineAxis(i,name);
    // add rec to definition
    axis_recs().put(i,rec);
  }
  // fill remainder with default definitions
  for( ; i<MaxAxis; i++ )
  {
    defineAxis(i,AtomicID(i));
    axis_recs().put(i,new DMI::Record);
  }
  _default_mapping = false;
}


// init default map of TIME/FREQ
static int initDefaultMaps ()
{
  axis_recs <<= new DMI::Vec(TpDMIRecord,MaxAxis);
  axis_ids  <<= new DMI::Vec(TpDMIHIID,MaxAxis);
  
  const HIID defmap[] = { AidTime,AidFreq };
  setAxisMap(defmap,sizeof(defmap)/sizeof(defmap[0]));
  
  // reset default_mapping flag that was cleared by setAxisMap()
  _default_mapping = true;
  
  return 0;
}

// initialize the default map
static int dum = initDefaultMaps();


}}; // close both namespaces
  
