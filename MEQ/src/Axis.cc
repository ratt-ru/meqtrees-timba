#include <MEQ/AID-Meq.h>
#include <MEQ/Axis.h>

namespace Meq {
namespace Axis {
  
int FREQ = 0;
int TIME = 1;

// mappings between names and numbers
AtomicID _name_map[MaxAxis];
std::map<AtomicID,int> _num_map;

static int initDefaultMaps ()
{
  _num_map[ _name_map[0] = AidFreq ] = FREQ = 0;
  _num_map[ _name_map[1] = AidTime ] = TIME = 1;
  for( int i=2; i<MaxAxis; i++ )
    _num_map[ _name_map[i] = AtomicID(i) ] = i;
  return 0;
}

static int dum = initDefaultMaps();

template<class Iter>
void setAxisMap (Iter begin,Iter end)
{
  int i=0;
  for( ; begin<end; i++,begin++ )
  {
    FailWhen(i >= MaxAxis,"too many axes in problem space definition");
    AtomicID name = *begin;
    _name_map[i] = name;
    _num_map[name] = i;
    if( name == AidFreq )
      FREQ = i;
    else if( name == AidTime )
      TIME = i;
  }
  // fill the rest with numbers
  for( ; i<MaxAxis; i++ )
  {
    AtomicID name(i);
    _name_map[i] = name;
    _num_map[name] = i;
  } 
}

void setAxisMap (const HIID &map)
{
  setAxisMap(map.begin(),map.end());
}

void setAxisMap (const AtomicID names[],int num)
{
  setAxisMap(names,names+num);
}
  
}}; // close both namespaces
  
