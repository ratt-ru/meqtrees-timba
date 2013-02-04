//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include <TimBase/Thread/Thread.h>
#include <TimBase/Thread/Mutex.h>

#include <TimBase/CheckConfig.h>
#ifdef USE_THREADS
CHECK_CONFIG_CC(UseThreads,yes);
#include <map>
#else
CHECK_CONFIG_CC(UseThreads,no);
#endif

#include <config.h>

namespace LOFAR
{
  namespace Thread 
  {
    Debug::Context DebugContext("Thread");
  
#ifdef USE_THREADS
    void * dummy_pvoid;
    int dummy_int;
    const Attributes _null_attributes;
    
    Thread::Mutex thread_map_mutex_;
    std::map<ThrID,int> thread_map_;
    std::vector<ThrID> thread_list_;
    
    static inline ThrID mapThread (ThrID id)
    {
      thread_map_[id] = thread_list_.size(); 
      thread_list_.push_back(id);
      return id;
    }
    
    //  creates a thread
    ThrID create (void * (*start)(void*),void *arg,const Attributes &attr)
    { 
      Thread::Mutex::Lock lock(thread_map_mutex_);
      // if first time a new thread is created, then self() is the main thread,
      // so add it to the map
      if( thread_list_.empty() )
      {
        thread_list_.reserve(64);
        thread_map_[self()] = 0;
        thread_list_.push_back(self());
      }
      // create new thread
      pthread_t id = 0;
      pthread_create(&id,attr,start,arg);
      // add to map
      thread_map_[id] = thread_list_.size();
      thread_list_.push_back(id);
      return id;
    }
    
    // exits current thread
    void exit (void *value)
    { 
      pthread_exit(value); 
    }

    // rejoins thread
    int ThrID::join (void * &value)
    { 
      return pthread_join(id_,&value);  
    }
    
#endif

  } // namespace Thread

} // namespace LOFAR
