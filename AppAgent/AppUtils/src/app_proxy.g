###  app_proxy.g: application proxy class
###
###  Copyright (C) 2002-2003
###  ASTRON (Netherlands Foundation for Research in Astronomy)
###  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
###
###  This program is free software; you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation; either version 2 of the License, or
###  (at your option) any later version.
###
###  This program is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
###  GNU General Public License for more details.
###
###  You should have received a copy of the GNU General Public License
###  along with this program; if not, write to the Free Software
###  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###
###  $Id$
pragma include once

# print software version
if( has_field(lofar_software,'print_versions') &&
    lofar_software.print_versions )
{
  print '$Id$';
}

include 'widgetserver.g'
include 'octopussy.g'
include 'recutil.g'
include 'gui/text_frame.g'

default_octopussy := F;

# Starts a global octopussy proxy with the given arguments, 
# unless already started.
# Returns a ref to the proxy object.
const start_octopussy := function(server,options="",verbose=1)
{
  global default_octopussy;
  if( is_boolean(default_octopussy) )
  {
    default_octopussy := octopussy(server,options,verbose=verbose);
    if( is_fail(default_octopussy) )
      fail default_octopussy;
    print 'starting';
    default_octopussy.start();
    print 'started';
  }
  return ref default_octopussy;
}

const app_proxy := function (appid,
        server=F,options=F,verbose=1,
        gui=F,ref parent_frame=F,ref widgetset=dws,
        ref self = [=],ref public = [=])
{
  if( !has_field(self,'appid') )
    self.appid := appid;
  if( !has_field(public,'self') )
    public.self := ref self;
  # define standard debug methods
  define_debug_methods(self,public,verbose);
  # init octopussy
  self.octo := start_octopussy(server,options,verbose=verbose);
  if( is_fail(self.octo) )
    fail;
  # init everything else
  self.ws := ref widgetset;
  self.appid := appid;
  self.lappid := paste(split(to_lower(appid),'.'),sep='_');
  self.octoagent := ref self.octo.agentref();
  self.relay := create_agent();
  self.octo.subscribe(spaste(appid,".Out.*"));
  self.state := -1;
  self.paused := F;
  self.statestr := "unknown";
  self.verbose_events := T;
  self.error_log := [=];
  self.rqid := 1;
  self.waiting_init := F;
  self.last_cmd_arg := [=];
  self.parent_frame := ref parent_frame;
  # define default init record (specifically, its control part)
  self.initrec_prev := [ 
    control = [ event_map_in  = [ default_prefix = hiid(self.appid,"In") ],
                event_map_out = [ default_prefix = hiid(self.appid,"Out") ],
                stop_when_end = F ] ]; 
  # setup fail/exit handlers
  whenever self.octoagent->["fail done exit"] do 
  {
    public.dprint(1,'exit event: ',$name,$value);
    if( $name == 'fail' )
      msg := paste('client process has died unexpectedly: ',$name,$value);
    else
      msg := paste('client process has exited: ',$name,$value);
    self.relay->app_notify_state([state=-2,state_string=to_upper($name),text=msg]);
    self.octo := F;
    self.octoagent := F;
  }
  
  # define standard app proxy methods
  # allocates a new request-id
  const self.new_requestid := function ()
  {
    wider self;
    ret := self.rqid;
    self.rqid +:= 1;
    if( self.rqid <= 0 )
      self.rqid := 1;
    return ret;
  }
  # Returns the application name
  const public.appid := function ()
  {
    wider self;
    return self.appid;
  }
  # Enables or disables verbose event reports. With no arguments,
  # returns current setting
  const public.verbose_events := function (verb=-1)
  {
    wider self;
    if( is_boolean(verb) )
      self.verbose_events := verb;
    return self.verbose_events;
  }
  const public.setdebug := function(context,level)
  {
    wider self;
    return self.octo.setdebug(context,level);
  }
  # Creates an event name by prefixing it with "appname_"
  const public.eventname := function (...)
  {
    wider self;
    return paste(self.lappid,...,sep="_");
  }
  # Returns a ref to the octopussy proxy
  const public.octo := function ()
  {
    wider self;
    return ref self.octo;
  }
  # Returns a ref to octopussy's agent
  const public.octoagent := function ()
  {
    wider self;
    return ref self.octoagent;
  }
  # Returns a ref to the local relay agent
  const public.relay := function ()
  {
    wider self;
    return ref self.relay;
  }
  const public.get_default_args := function (command)
  {
    if( has_field(self.last_cmd_arg,command) )
      return self.last_cmd_arg[command];
    else
      return [=];
  }
  const public.set_default_args := function (command,data,update_gui=T)
  {
    wider self;
    self.last_cmd_arg[command] := data;
    if( update_gui )
      self.update_command_dialog(command,data);
  }
  # Sends an app control command to the app
  const public.command := function (message,payload=F,update_gui=T,set_default=F,priority=5)
  {
    wider self;
    wider public;
    public.set_default_args(message,payload);
    if( !set_default )
    {
      # report as event to relay
      self.relay->[spaste('sending_command_',message)](payload);
      return self.octo.publish(spaste(self.appid,".In.App.Control.",message),
                  priority=priority,
                  rec=payload);
    }
  }
  # Initializes the app. All four of the records may be supplied,
  # or any may be omitted to reuse the old record
  # If wait=T, waits for the app to complete init
  const public.init := function (initrec=F,input=F,output=F,control=F,wait=F)
  {
    wider public;
    wider self;
    # if initrec is not specified, reuse previous one, if available
    if( !is_record(initrec) )
    {
      if( !is_record(self.initrec_prev) )
        fail 'no previous init record specified';
      initrec := self.initrec_prev;
      self.dprint(2,'init: reusing previous initrec');
    }
    # if some subrecords are missing, reuse previous ones 
    print initrec;
    subrecs := [ input=ref input,output=ref output,control=ref control ];
    for( f in field_names(subrecs) )
    {
      if( is_record(subrecs[f]) )
      {
        initrec[f] := subrecs[f];
        self.dprintf(2,'init: using %s subrec from parameters',f);
      }
      else
      {
        if( has_field(initrec,f) )
          self.dprintf(2,'init: initrec contains %s rec',f);
        else
        {
          if( has_field(self.initrec_prev,f) )
          {
            initrec[f] := self.initrec_prev[f];
            self.dprintf(2,'init: using previous %s rec',f);
          }
        }
      }
    }
    self.initrec_prev := initrec;
    self.dprint(3,'init: initrec is ',initrec);
    self.waiting_init := T;
    self.dprint(2,'init: will await init completion');
    res := public.command("Init",initrec);
    if( is_fail(res) )
      fail;
    if( wait )
    {
      while( self.waiting_init )
      {
        await self.relay->*;
        self.dprint(2,'init: got event ',$name);
      }
      self.dprint(2,'init: wait complete');
    }
  }
  # Shortcuts for sending various commands to the app
  const public.stop := function (from_gui=F)
  {
    wider public;
    public.command("Stop");
  }
  const public.halt := function (from_gui=F)
  {
    wider public;
    public.command("Halt");
  }
  const public.pause := function (from_gui=F)
  {
    wider public;
    public.command("Pause");
  }
  public.resume := function (rec=F,from_gui=F)
  {
    wider public;
    wider self;
    public.command("Resume",rec,priority=10);
  }
  # Logs an error
  const self.log_error := function (event,error)
  {
    wider self;
    self.error_log[len(self.error_log)+1] := [event=event,error=error];
  }
  # Returns number of accumulated errors
  const public.num_errors := function ()
  {
    wider self;
    return len(self.error_log);
  }
  # Returns log of accumulated errors, clears the error log if clear=T
  const public.get_error_log := function (clear=T)
  {
    wider self;
    log := self.error_log;
    if( clear )
      self.error_log := [=];
    return log;
  }
  # Returns current state, pause state and state string
  const public.state := function ()
  {
    wider self;
    return self.state;
  }
  const public.is_paused := function ()
  {
    wider self;
    return self.paused;
  }
  const public.strstate := function ()
  {
    wider self;
    return self.statestr;
  }
  # Requests a full status record from the app
  const public.reqstatus := function ()
  {
    wider public;
    public.command("Request.Status");
  }
  # Requests a specific field of the status record from the app
  const public.status := function (subfield=F)
  {
    wider public;
    wider self;
    rqid := self.new_requestid();
    rec := [ request_id = hiid(rqid) ];
    evname := public.eventname('out_app_status',rqid);
    if( subfield )
      rec.field := hiid(subfield);
    public.command("Request.Status",rec);
    await self.octoagent->[evname];
    return $value.value;
  }
  const public.notify := function (...)
  {
    wider self;
    self.relay->notify_message([text=spaste(...)]);
  }
  
  if( !has_field(self,'gui_event_handlers') )
    self.gui_event_handlers := [=];
  self.gui_event_handlers.app_proxy := function (name,value)
  {
    wider self;
    if( name == 'kill_gui' )
    {
      self.dprint(1,'got kill_gui event, deactivating gui');
      return F;  # this will deactivate the gui
    }
    name0 := name;    # store old value since regex below changes name
    report := T;      # will it be reported to the event log?
    if( name ~ m/^sending_command_/ )
      report := F;
    # update state
    else if( name == 'app_notify_state' ) 
    {
      self.gui.state->delete('0','end');
      self.gui.state->insert(value.state_string);
      self.gui.pause->relief('raised');
      self.gui.pause->disabled(value.paused);
      self.gui.resume->disabled(!value.paused);
    }
    # update status record
    else if( name =~ s/^app_update_status_// )
    {
      name := split(name,'/');
      if( len(name) == 1 )
      {
        self.gui.statusrec[name] := [=];
        for( f in field_names(value) )
          self.gui.statusrec[f] := value[f];
      }
      else
      {
        if( !has_field(self.gui.statusrec,name[1]) ||
            !is_record(self.gui.statusrec[name[1]]) )
          self.gui.statusrec[name[1]] := [=];
        for( f in field_names(value[name[1]]) )
          self.gui.statusrec[name[1]][f] := value[name[1]][f];
      }
      self.gui.statusbrowser->newrecord(self.gui.statusrec);
      report := F;
    }
    else if( name ~ m/^app_status/ )
    {
      self.gui.statusrec := value.value;
      self.gui.statusbrowser->newrecord(self.gui.statusrec);
      report := F;
    }
    # update event log
    if( report )
    {
      str := sprintf('%.120s\n',spaste(name0,': ',value));
      self.gui.eventlog.text->append(str,'event');
      for( f in "error message text" )
        if( has_field(value,f) )
        {
          if( f == 'error' )
            tag := 'error';
          else
            tag := 'text';
          self.gui.eventlog.text->append(spaste(value[f],'\n'),tag);
          break;
        }
    }
    return T;
  }
  
  const self.update_command_dialog := function (command,payload)
  {
    wider self;
    if( has_field(self,'gui') && has_field(self.gui,'dialog') &&
        has_field(self.gui.dialog,command) )
    {
      text := val2string(payload,skip_braces=T);
      self.gui.dialog[command].browser.settext(paste(text,sep='\n'));
    }
  }
  const self.make_command_dialog := function (name,command,button=F,size=[40,20])
  {
    wider self;
    rec := [=];
    rec.topfr := self.ws.frame(parent=F,title=spaste(self.appid,': ',name),
                            tlead=button,relief='ridge');
    rec.topfr->unmap();
    
    rec.label := self.ws.label(rec.topfr,paste(self.appid,': ',name));
    if( has_field(self.last_cmd_arg,command) )
      text := paste(val2string(self.last_cmd_arg[command],skip_braces=T),sep='\n'); 
    else
      text := '';
    rec.browser := text_frame(rec.topfr,disabled=F,
                              size=size,text=text,ws=self.ws);
    rec.browser.text->see('0,0');
    rec.cmdframe := self.ws.frame(parent=rec.topfr,side='left',expand='none');
    rec.accept := self.ws.button(rec.cmdframe,to_upper(name));
    rec.reset  := self.ws.button(rec.cmdframe,'Reset');
    rec.cancel := self.ws.button(rec.cmdframe,'Cancel');
    
    rec.error := self.ws.frame(parent=F,tlead=rec.topfr,tpos='c',relief='ridge');
    rec.error->unmap();
    rec.error_msg := self.ws.label(rec.error,'Failed to parse input record');
    rec.error_dismiss := self.ws.button(rec.error,'Dismiss');
    
    whenever rec.error_dismiss->press do 
    { 
#      rec.error->release();
      rec.error->unmap();
#      rec.topfr->grab('local');
      rec.topfr->enable();
    }
    whenever rec.cancel->press do 
    {
#      rec.topfr->release();
      rec.topfr->unmap();
      self.gui.topframe->enable();
    }
    whenever rec.reset->press do
    {
      if( has_field(self.last_cmd_arg,command) )
        text := paste(val2string(self.last_cmd_arg[command],skip_braces=T),sep='\n'); 
      else
        text := '';
      rec.browser.settext(text);
    }
    whenever rec.accept->press do 
    {
      str := rec.browser.text->get('0.0','end');
      data := string2val(str);
      # failed conversion?
      if( is_fail(data) )
      {
#        rec.topfr->release();
        rec.topfr->disable();
        for( f in "map raise enable" )
          rec.error->[f]();
      }
      else
      {
        public.command(command,data,update_gui=F);
#        rec.topfr->release();
        rec.topfr->unmap();
        self.gui.topframe->enable();
      }
    }
    # setup event handler for parent button
    if( !is_boolean(button) )
    {
      whenever button->press do 
      {
        self.gui.topframe->disable();
        for( f in "map raise enable" )
          rec.topfr->[f]();
      }
    }
    self.gui.dialog[command] := rec;
  }
  const self.make_gui := function (title)
  {
    wider self;
    wider public;
    if( !is_record(self.ws) ) fail 'widgetset not specified in constructor';
    if( is_record(self.gui) ) fail 'gui frame already constructed';
    self.gui := [=];
    # try to create top-level frame with existing parent (if set)
#   print 'parent: ',self.parent_frame,is_agent(self.parent_frame);
    self.gui.topframe := self.ws.frame(parent=self.parent_frame,
                                       title=title,relief='groove');
    # if that fails, we can try again w/o a parent
    if( is_fail(self.gui.topframe) )
    {
      if( is_boolean(self.parent_frame) )
        fail;
      self.dprint(1,'gui frame creation failed');
      self.dprint(1,'possibly the parent frame has been killed');
      self.dprint(1,'re-trying without a parent frame');
      self.parent_frame := F;
      self.gui.topframe := self.ws.frame(title=title,relief='groove');
    }
    self.gui.topframe->unmap();
    self.gui.killflag := F;
    # create state window
    self.gui.stateframe := self.ws.frame(parent=self.gui.topframe,side='left',expand='none');
    self.gui.state_lbl := self.ws.label(self.gui.stateframe,spaste(self.appid,': '));
    self.gui.state := self.ws.entry(self.gui.stateframe,width=30,
                               relief='sunken',disabled=T);
    # create command buttons
    self.gui.cmd_frame := self.ws.frame(parent=self.gui.topframe,side='left',expand='none');
    self.gui.pause := self.ws.button(self.gui.cmd_frame,'PAUSE',disabled=T);
    self.gui.resume := self.ws.button(self.gui.cmd_frame,'RESUME',disabled=T);
    self.gui.updstatus := self.ws.button(self.gui.cmd_frame,'Update status');
    self.gui.resume_pad := self.ws.frame(self.gui.cmd_frame,expand='none',width=20,height=5);
    self.gui.init := self.ws.button(self.gui.cmd_frame,'INIT');
    self.make_command_dialog('Init','Init',self.gui.init);
    self.gui.stop := self.ws.button(self.gui.cmd_frame,'STOP');
    self.gui.stop_pad := self.ws.frame(self.gui.cmd_frame,expand='none',width=20,height=5);
    self.gui.halt := self.ws.button(self.gui.cmd_frame,'HALT');
    # register event handlers for command buttons
    whenever self.gui.pause->press do 
    { self.gui.pause->relief('sunken'); public.pause(from_gui=T); }
    whenever self.gui.resume->press do public.resume(from_gui=T);
    whenever self.gui.stop->press do public.stop(from_gui=T);
    whenever self.gui.halt->press do public.halt(from_gui=T);
    # create event logger
    self.gui.eventlog := text_frame(self.gui.topframe,disabled=T,size=[60,20],
                                    ws=self.ws);
    self.gui.eventlog.text->config('event',foreground="#808080");
    self.gui.eventlog.text->config('text',foreground="black");
    self.gui.eventlog.text->config('error',foreground="red");
    # create second command panel
    self.gui.cmd2_frame := self.ws.frame(parent=self.gui.topframe,side='right',expand='none');
    self.gui.updstatus := self.ws.button(self.gui.cmd2_frame,'Update status');
    # create status record panel
    self.gui.statusbrowser := self.ws.recordbrowser(self.gui.topframe,[status='none']);
    self.gui.statusrec := [=];
    whenever self.gui.updstatus->press do public.reqstatus();
    # add extra gui elements (if supplied by child classes)
    if( is_record(self.make_extra_gui) )
    {
      for( f in field_names(self.make_extra_gui) )
        self.make_extra_gui[f](enable=T);
    }
    # handle killed events from top frame
    whenever self.gui.topframe->killed do 
    { 
      deactivate;
      self.dprint(2,'got "killed" event from topframe');
      public.kill_gui();
    }
    self.gui.whenever_killed := last_whenever_executed();
    if( is_agent(self.parent_frame) )
    {
      whenever self.parent_frame->killed do 
      {
        deactivate;
        self.dprint(2,'got "killed" event from parent');
        public.kill_gui();
      }
      self.gui.whenever_killed := [self.gui.whenever_killed,last_whenever_executed()];
    }
    # create event handler to update the GUI
    whenever self.relay->* do
    {
      # deactivate if gui had been destroyed
      if( !is_record(self.gui) )
      {
        self.dprint(1,'hmmm, no gui, deactivating event handler');
        deactivate;
      }
      else
      {
        for( f in field_names(self.gui_event_handlers) )
          if( !self.gui_event_handlers[f]($name,$value) )
          {
            deactivate;
            deactivate self.gui.whenever_killed;
            self.gui.topframe->unmap();
            # destroy any extra gui elements
            for( f in field_names(self.make_extra_gui) )
              self.make_extra_gui[f](enable=F);
            # destroy sub-widgets that require special treatment
            for( f in field_names(self.gui.dialog) )
            {
              self.gui.dialog[f].topfr->unmap();
              self.gui.dialog[f].topfr := F;
            }
            if( is_agent(self.gui.statusbrowser) )
              self.gui.statusbrowser->close();
            self.gui.eventlog.done()
            self.gui.topframe := F;
            self.gui := F;
            break;
          }
      }
    }
    self.gui.event_handler_id := last_whenever_executed();
    self.gui.topframe->map();
    return ref self.gui.topframe;
  }
  const public.kill_gui := function ()
  {
    wider self;
    if( !is_record(self.gui) )
      return T;
    self.gui.killflag := T;
    self.dprint(1,'enqueueing kill_gui event');
    self.relay->kill_gui();
    return T;
  }
  const public.gui := function (enable=T,ref parent=F,ref widgetset=F,title=F)
  {
    wider self;
    # enable=F: unmap gui, if any
    if( !enable )
    {
      if( has_field(self.gui,'topframe') )
        self.gui.topframe->unmap();
      return T;
    }
    # gui exists but is being destroyed -- flush events, it ought to die
    if( is_record(self.gui) && self.gui.killflag )
    {
      self.dprint(1,'waiting for previous gui to die');
      flush_events(self.relay);
    }
    # gui exists, so just map it
    if( is_record(self.gui) )
    {
      self.dprint(1,'gui already constructed, mapping');
      self.gui.topframe->map();
      return ref self.gui.topframe;
    }
    # no gui: construct it
    # override various parameters, if asked to do so
    if( is_agent(parent) )
      self.parent_frame := ref parent;
    if( is_agent(widgetset) )
      self.ws := ref widgetset;
    if( is_boolean(title) )
      title := self.appid;
    return ref self.make_gui(title);
  }
  
  # register global event handler for this app -- all "our" events are
  # relayed to the relay agent
  whenever self.octoagent->* do
  {
    self.dprint(5,"original event: ",$name);
    # check that event is intended for us
    shortname := eval(spaste("'",$name,"'~s/^",self.lappid,"_out_//"));
    self.dprint(5,"short event name: ",shortname);
    if( shortname != $name )
    {
      # process state events
      if( shortname == 'app_notify_state' )
      {
        self.dprint(1,$value.state_string,' (',$value.state,')');
        self.state := $value.state;
        self.paused := $value.paused;
        self.statestr := $value.state_string;
      }
      else if( shortname == 'app_notify_init' )
      {
        self.waiting_init := F;
      }
      # accumulate error events
      if( has_field($value,'error') )
        self.log_error(shortname,$value.error);
      # print events if so requested
      if( self.verbose_events )
      {
        public.dprint(2,'   event: ', shortname);
        public.dprint(3,'   value: ', $value);
      }
      # if event has a text, message or error component, print it
      for( f in "text message error" )
        if( has_field($value,f) )
          public.dprint(1,'[',f,'] ',$value[f]); 
      # forward event to local relay agent
      $value::event_name := shortname;
      self.relay->[shortname]($value);
    }
  }
  # create gui if asked to do so
  if( gui )
    public.gui()
  
  return ref public;
}

