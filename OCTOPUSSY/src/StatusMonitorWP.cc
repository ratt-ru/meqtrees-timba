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

#include "StatusMonitorWP.h"

#include <sys/time.h>
#include <sys/resource.h>
#include <unistd.h>


namespace Octopussy
{

StatusMonitorWP::StatusMonitorWP (int ms,AtomicID wpid)
 : WorkProcess(wpid),
   period_ms_(ms),
   prefix_("Process.Status")
{
  pagesize_ = sysconf(_SC_PAGESIZE)>>10;
}

StatusMonitorWP::~StatusMonitorWP()
{
}

//##ModelId=3C7E4AC70261
bool StatusMonitorWP::start ()
{
  WorkProcess::start();
  if( period_ms_ )
    addTimeout(period_ms_*1e-3,AidBroadcast,EV_CONT);
  return false;
}

void StatusMonitorWP::setPeriod (int ms)
{
  if( isRunning() )
  {
    if( period_ms_ )
      removeTimeout(AidBroadcast);
    addTimeout((period_ms_=ms)*1e-3,AidBroadcast,EV_CONT);
  }
  else
    period_ms_ = ms;
}

void StatusMonitorWP::makeStatusMessage (Message::Ref &msg)
{
//   // get limits
//   struct rlimit rlim_data;
//   struct rlimit rlim_rss;
//   getrlimit(RLIMIT_DATA,&rlim_data);
//   getrlimit(RLIMIT_RSS,&rlim_rss);
  // get memory status
  int tot_pg=0,mem_pg=0,shared_pg=0,code_pg=0,data_pg=0,lib_pg=0,dirty_pg=0;
  FILE *fs = fopen("/proc/self/statm","r");
  if( fs )
  {
    fscanf(fs,"%d %d %d %d %d %d %d",&tot_pg,&mem_pg,&shared_pg,&code_pg,&data_pg,&lib_pg,&dirty_pg);
    fclose(fs);
  }
  // get cpu time usage
  struct rusage ru;
  getrusage(RUSAGE_SELF,&ru);
  // form message
  HIID msgid = prefix_;
  int i = prefix_.size();
  msgid.resize(i+11);
  msgid[i++] = tot_pg*pagesize_;
  msgid[i++] = mem_pg*pagesize_;
  msgid[i++] = shared_pg*pagesize_;
  msgid[i++] = code_pg*pagesize_;
  msgid[i++] = data_pg*pagesize_;
  msgid[i++] = lib_pg*pagesize_;
  msgid[i++] = dirty_pg*pagesize_;
  msgid[i++] = ru.ru_utime.tv_sec;
  msgid[i++] = ru.ru_utime.tv_usec;
  msgid[i++] = ru.ru_stime.tv_sec;
  msgid[i++] = ru.ru_stime.tv_usec;
  // create message 
  msg <<= new Message(msgid);
}

int StatusMonitorWP::timeout (const HIID &)
{
  Message::Ref msg;
  makeStatusMessage(msg);
  // send it off
  publish(msg);
  return Message::ACCEPT;
}

//##ModelId=3C7E49AC014C
int StatusMonitorWP::receive (Message::Ref& mref)
{
  // print the message starting at debug level 2
  if( Debug(2) )
  {
    int level = getDebugContext().level() - 1;
    dprintf(2)("received: %s\n",mref->sdebug(level).c_str());
  }
  // process message
  const HIID &id = mref->id();
  if( id.matches("Set.Period.?") )
  {
    setPeriod(id[2]);
  }
  else if( id.matches("Request") )
  {
    Message::Ref response;
    makeStatusMessage(response);
    send(response,mref->from());
  }
  return Message::ACCEPT;
}

};
