//  MSVisOutputAgent.h: agent for writing an AIPS++ MS
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#ifndef MSVISAGENT_SRC_MSOUTPUTCHANNEL_H_HEADER_INCLUDED_F5146265
#define MSVISAGENT_SRC_MSOUTPUTCHANNEL_H_HEADER_INCLUDED_F5146265
    
#include <AppAgent/FileChannel.h>
#include <AppUtils/MSChannelDebugContext.h>
#include <AppUtils/MSChannelVocabulary.h>
#include <VisCube/VisVocabulary.h>
#include <VisCube/VTile.h>

#include <ms/MeasurementSets/MeasurementSet.h>
#include <casa/Arrays/Slicer.h>
#include <casa/Arrays/Array.h>
#include <tables/Tables/ArrayColumn.h>
#include <tables/Tables/ScalarColumn.h>

namespace AppAgent
{
using namespace DMI;
  
using namespace VisCube;
using namespace VisVocabulary;

//##ModelId=3E02FF340070
class MSOutputChannel : public FileChannel
{
  public:
    //##ModelId=3E2831C7010D
    MSOutputChannel ();

    //##ModelId=3E28315F0001
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitializean agent. Agent parameters are supplied via a
    //## DMI::Record.
    virtual int init(const DMI::Record &data);

    //##ModelId=3E283161032B
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
    virtual void close(const string &str="");

    //##ModelId=3EC25BF002D4
    //##Documentation
    //## Posts an event on behalf of the application.
    //## If a non-empty destination is specified, the event is directed at
    //## a specific destination, if the event channel implementation supports
    //## this (e.g., if responding to a request event, destination could be
    //## equal to the original event source).
    virtual void postEvent(const HIID &id, const ObjRef &data = ObjRef(),AtomicID cat=AidNormal,const HIID &destination = HIID());

    //##ModelId=3EC25BF002E4
    //##Documentation
    //## Checks whether a specific event is bound to any output. I.e., if the
    //## event would be simply discarded when posted, returns false; otherwise,
    //## returns true. Apps can check this before posting "expensive" events.
    //## Default implementation always returns false.
    virtual bool isEventBound(const HIID &id,AtomicID cat=AidNormal);
    
    //##ModelId=3E283172001B
    string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    
    //##ModelId=400E5B6C00EC
    ImportDebugContext(MSChannelDebugContext);
    
  protected:
    //## closes and detaches from the MS
    void close_ms ();
      
      
    //##ModelId=3EC25F74033F
    //##Documentation
    //## called to put more objects on the stream. Returns SUCCESS if something
    //## was put on, or <0 code (ERROR/CLOSED/whatever)
    virtual int refillStream();

    //##ModelId=3E2ED3290292
    typedef struct 
    {
      string name;
      casa::ArrayColumn<casa::Complex> col;
      bool   valid;
    }
    Column;
    
    //##ModelId=3E2831C7011D
    MSOutputChannel(const MSOutputChannel& right);

    //##ModelId=3E2831C70155
    MSOutputChannel& operator=(const MSOutputChannel& right);
    
    //##ModelId=3E2D73EB00CE
    bool setupDataColumn (Column &col);

    //##ModelId=3E28316403E4
    //##Documentation
    //## Puts visibilities header onto output stream. If stream has been
    //## suspended (i.e. from other end), returns WAIT (wait=false), or
    //## blocks until it is resumed (wait=true)
    //## Returns: SUCCESS   on success
    //##          WAIT      stream has been suspended from other end
    //##          CLOSED    stream closed
    virtual void doPutHeader(const DMI::Record &header);

    //##ModelId=3E28316B012D
    //##Documentation
    //## Puts next tile onto output stream. If stream has been
    //## suspended (i.e. from other end), returns WAIT (wait=false), or
    //## blocks until it is resumed (wait=true)
    //## Returns: SUCCESS   on success
    //##          WAIT      stream has been suspended from other end    
    //##          CLOSED    stream closed
    virtual void doPutTile (const VTile &tile);
    
    
    virtual void doPutFooter (const DMI::Record &footer);

    //##ModelId=3F5F436303AB
    void putColumn (Column &col,int irow,const LoMat_fcomplex &data);
    
    //##ModelId=3E2D6130030C
    string msname_;
        
    //##ModelId=3E2BC34C0076
    casa::MeasurementSet ms_;
    
    //##ModelId=3E2D5FF503A1
    DMI::Record params_;
    
    //##ModelId=3E2D5FF60047
    bool write_flags_;
    //##ModelId=3E2D5FF600B0
    int flagmask_;
    
    //##ModelId=3E2D61D901E8
    int tilecount_;
    //##ModelId=3E2D61D9024A
    int rowcount_;
    
    bool flip_freq_;
    
    int channels_[2];
    int chan_incr_;

    //##ModelId=3E2D5FF60119
    casa::Slicer column_slicer_;
    
    //##ModelId=3E42745300A8
    Column datacol_;
    //##ModelId=3E42745300C2
    Column predictcol_;
    //##ModelId=3E42745300DA
    Column rescol_;
    
    //##ModelId=3E2ED50E0113
    casa::ScalarColumn<casa::Bool> rowFlagCol_;
    //##ModelId=3E2ED50E0190
    casa::ArrayColumn<casa::Bool> flagCol_;
    
    //##ModelId=3F5F43630379
    casa::Array<casa::Complex> null_cell_;
};


} // namespace AppAgent
#endif /* MSVISAGENT_SRC_MSVISOUTPUTAGENT_H_HEADER_INCLUDED_F5146265 */
