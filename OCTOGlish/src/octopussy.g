###  octopussy.g: Glish interface to OCTOPUSSY
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

include 'note.g'
include 'debug_methods.g'
include 'dmitypes.g'

const define_octoserver := function (connpath,binary='',
  options="",autostart=T,nostart=F,valgrind=F,opt=F,valgrind_opts="")
{
  server := [ connpath=connpath,binary=binary,options=options,
              autostart=autostart,nostart=nostart,opt=opt ];
  if( !is_boolean(valgrind) || valgrind )
  {
    server.valgrind := T;
    if( is_string(valgrind) )
      server.valgrind_options := valgrind;
    else
      server.valgrind_options := [ _default_valgrind_options,valgrind_opts ];
  }
  return server;
}

const default_octoserver_fifo := spaste('/tmp/octoglish-',environ.USER);

const default_octoserver := define_octoserver(default_octoserver_fifo,
  'octoglishserver');

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------
const octopussy := function (server=default_octoserver,options="",
                             autoexit=T,verbose=1)
{
  self := [=];
  public := [=];

  self.send_client := self.rcv_client := F
  self.rcv_client::Connected := self.send_client::Connected := F;
  self.state := 0;
  self.started := F;
  # this should be consistent with PRI_NORMAL in OCTOPUSSY/Message.h, and
  # is used as the baseline priority value. The priority parameters
  # used below are added to this value
  self.priority_normal := 256;
  self.appid := 'octopussy';
  
  define_debug_methods(self,public,verbose);

  const self.makeclient := function (server,options="")
  {
    wider self;
    self.connected := F;
    # check for pipe file
    fifo := server.connpath;
    server_autostart := F;
    pipe_existed := ( len(fifo) > 0 && len(stat(fifo)) > 0 );
    if( pipe_existed )
    {
      self.dprint(2,'fifo ',fifo,' is present');
      # check for running server, if we know the name
      if( len(server.binary) && server.autostart )
      {
        regex := s/.*\///g;
        binfile := server.binary ~ regex;
        self.dprint(2,'checking for running ',binfile);
        out := shell(paste('pgrep -u',environ.USER,binfile)); 
        if( len(out)>0 )
          self.dprint(0,'server running: ',out[1]);
        else
        {
          server_autostart := T;
          self.dprint(0,'server ',binfile,' does not appear to be running');
        }
      }
    }
    else
      self.dprint(1,'fifo ',fifo,' is not available');
    # run server if no pipe file, or server is missing
    if( !pipe_existed || server_autostart || server.nostart )
    {
      if( !len(server.binary) && !server.nostart )
      {
        self.dprint(1,'fail: no server binary specified');
        fail 'server path not available, and no server binary specified';
      }
      # try to start a server
      # make use of options attribute, if defined
      binname := server.binary;
      if( server.opt )
        binname := spaste(binname,'-opt');
        
      cmd := paste(binname,server.options,options);
      
      if( has_field(server,'valgrind') && server.valgrind ) # start under valgrind -- some trickery required
      {
        if( has_field(server,'valgrind_options') && is_string(server.valgrind_options) )
          valopt := server.valgrind_options;
        else
          valopt := '';
        cmd := paste('valgrind',valopt,cmd);
      }
      cmd =~ s/([<>*])/\\$1/g;
      # start the server, or ask user to start the server
      if( server.nostart )
      {
        print '===============================================';
        print '=== Waiting for server to be manually started'
        print '=== Please start it with the following command:';
        print '===',cmd;
        print '===============================================';
        # wait for pipe to appear
        while( !len(stat(fifo)) )
          shell("sleep 1");
      }
      else # start the server as an async shell command
      {
        self.dprint(1,'starting server and waiting for [PIPE] spec');
        self.dprint(1,'command is: ',cmd);
        self.shell_client := shell(cmd,async=T);
        if( is_fail(self.shell_client) )
        {
          self.dprint(1,'server startup failed');
          fail;
        }
        # set a whenever to analyze server output
        whenever self.shell_client->* do
        {
          self.dprint(2,'shell_client event ',$name,': ',$value);
          if( $name == 'fail' || $name == 'done' )
            self.shell_client::Died := T;
          if( $name == 'stdout' && $value =~ s/\[PIPE\](.*)\[\/PIPE\]/$1/g )
          {
            self.shell_client::Pipe := $value;
            self.shell_client::HasPipe := T;
          }
        }
        # wait for server to succeed or fail
        while( !self.shell_client::HasPipe && !self.shell_client::Died )
          await self.shell_client->*;
        # have we got a pipe?
        if( self.shell_client::HasPipe )
        {
          fifo := self.shell_client::Pipe;
          self.dprint(1,'server ready with fifo name ',fifo);
        }
        else
        {
          self.dprint(1,'server startup failed');
          fail 'server startup has failed';
        }
      }
    }
    # check that pipe is of the right type
    if( stat(fifo).type != 'fifo' )
    {
      self.dprint(1,'fail: ',fifo,' is not a fifo');
      fail 'server path not fifo';
    }
    self.dprint(2,'opening fifo ',fifo,'...');
    # open file and write a connection request
    fifo_file := open(spaste('>',fifo));
    if( is_fail(fifo_file) )
    {
      self.dprint(1,'fail: can\'t open fifo ',fifo);
      fail;
    }
    self.dprint(2,'fifo open');
    # start the two clients in async mode  
    self.rcv_client  := client('dum',async=T);
    self.send_client := client('dum',async=T);
    # use attributes of agents for extra info
    self.rcv_client::Name := 'rcv_client';
    self.send_client::Name := 'send_client';
    self.rcv_client::Connected := F;
    self.send_client::Connected := F;
    # write agent startup arguments to pipe, hopefully this will
    # cause the server to create end-points for the agents
    write(fifo_file, 
      spaste('[CONNECTION]',
        paste(self.rcv_client.activate,sep='\t'),
        '\n',
        paste(self.send_client.activate,sep='\t'),
        '[/CONNECTION]'));
    fifo_file := F;
    # setup handler for connection events
    whenever self.rcv_client->established,self.send_client->established do 
    {
      $agent::Connected := T;
      self.dprint(2,$agent::Name,' is connected');
    }
    # set up fail/exit handler
    whenever self.rcv_client->["fail done"],self.send_client->["fail done"] do 
    {
      self.connected := $agent::Connected := F;
      self.dprint(1,$agent::Name,' has terminated with event ',$name,$value);
    }
    # await startup
    self.dprint(2,'waiting for both agents to connect');
    while( !(self.rcv_client::Connected) || !(self.send_client::Connected) )
      await self.rcv_client->*,self.send_client->*;
    self.connected := T;
    self.dprint(1,'octopussy proxy is ready');
    return T;
  }
  
  const self.makemsg := function (id,rec=F,priority=0,datablock=F,blockset=F)
  {
    wider self;
    data := [=];
    if( !is_boolean(rec) )
    {
      if( !is_boolean(blockset) )
        fail 'unable to send record and blockset together';
      data := rec;
      data::payload := "DataRecord";
    }
    else if( !is_boolean(blockset) )
    {
      # NB: check for blocktype
      data := blockset;
      data::payload := blockset::blocktype;
    }
    if( !is_boolean(datablock) )
    {
      data::datablock := datablock;
    }
    data::id := id;
    data::priority := self.priority_normal+priority;
    data::state := self.state;
    return data;
  }
  
  const self.getscope := function (scope)
  {
    sc := to_lower(scope);
    if( sc == "local" || sc == "process" )
      return 0;
    else if( sc == "host" )
      return 1;
    else if( sc == "global" )
      return 2;
    fail paste('illegal scope',scope);
  }

  
# Public functions
#------------------------------------------------------------------------------
  const public.init := function (server="",options="") 
  {
    wider self;
    if( !is_agent(self.rcv_client) || !is_agent(self.send_client) )
      return self.makeclient(server,options);
    return T;
  }

  const public.done := function () 
  {
    self.rcv_client->terminate();
    self.send_client->terminate();
    return T;
  }
  
  const public.subscribe := function (ids,scope="global")
  {
    # set the scope parameter
    wider self;
    sc := self.getscope(scope);
    if( is_fail(sc) )
      fail sc;
    for( id in ids )
    {
      self.dprint(2,"subscribing: ",id,sc);
      # send event
      if( !self.send_client->subscribe([id=id,scope=sc]) )
        fail 'subscribe() failed';
    }
    return T;
  }

  const public.unsubscribe := function (id)
  {
    wider self;
    if( self.send_client->unsubscribe([id=id]) )
      return T;
    else
      fail 'unsubscribe() failed';
  }
  
  const public.start := function ()
  {
    wider self;
    if( self.started  )
      fail 'octopussy already started';
    if( self.send_client->start([=]) )
    {
      self.started := T;
      return T;
    }
    else
      fail 'start() failed';
  }

  const public.log := function (msg,type="normal",level=1)
  {
    wider self;
    # check that we're started
    if( !self.started )
      fail 'octopussy not started';
    # set the type
    tp := to_lower(type);
    if( tp == "normal" )
      tp := "LogNormal";
    else if( tp == "warn" || tp == "warning" )
      tp := "LogWarning";
    else if( tp == "error" )
      tp := "LogError";
    else if( tp == "debug" )
      tp := "LogDebug";
    else if( tp == "fatal" )
      tp := "LogFatal";
    else
      fail paste('unknown log message type: ',type);
    # send the event
    if( self.send_client->log([msg=msg,level=level,type=tp]) )
      return T;
    else
      fail 'log() failed';
  }
  
  const public.send := function (id,dest,rec=F,priority=0,datablock=F,blockset=F)
  {
    wider self;
    # check that we're started
    if( !self.started )
      fail 'octopussy not started';
    rec := self.makemsg(id,rec,priority,datablock,blockset);
    rec::to := dest;
    # send the event
    if( self.send_client->send(rec) )
      return T;
    else
      fail 'send() failed';
  }

  const public.publish := function (id,rec=F,scope="global",priority=0,datablock=F,blockset=F)
  {
    wider self;
    # check that we're started
    if( !self.started )
      fail 'octopussy not started';
    # set the scope
    self.dprint(3,"publish: ",id,scope);
    sc := self.getscope(scope);
    if( is_fail(sc) )
      return sc;
    # create message record
    rec := self.makemsg(id,rec,priority,datablock,blockset);
    rec::scope := sc;
    self.dprint(3,"publishing: ",rec::);
    # send the event
    if( self.send_client->publish(rec) )
      return T;
    else
      fail 'publish() failed';
  }

  const public.receive := function (ref value)
  {
    wider self;
    # check that we're started
    if( !self.started )
      fail 'octopussy not started';
    # wait for message
    await self.rcv_client->*;
    val value := $value;
    self.dprint(3,"got event: ",$name);
    return $name;
  }
  
  const public.setdebug := function (context,level)
  {
    wider self;
    # check that we're started
    if( !self.started )
      fail 'octopussy not started';
    if( self.send_client->debug([context=context,level=level]) )
      return T;
    else
      fail 'setdebug failed'; 
  }
  
  const public.state := function ()
  {
    wider self;
    return self.state;
  }
  
  const public.setstate := function (newstate)
  {
    wider self;
    wider public;
    if( self.state != newstate )
    {
      self.state := newstate;
      return public.publish("WorkProcess.State");
    }
    return T;
  }
  
  const public.agentref := function ()
  {
    wider self;
    return ref self.rcv_client;
  }
  
  const public.connected := function ()
  {
    wider self;
    return self.connected;
  }
  
  const public.started := function ()
  {
    wider self;
    return self.started;
  }
  
  res := public.init(server,options);
  if( is_fail(res) )
  {
    self.dprint(0,'init failed');
    return res;
  }
  
  if( autoexit )
  {
    whenever self.rcv_client->["fail exit"] do 
    {
      self.dprint(0,"Got 'exit' event, auto-exit enabled, exiting");
      exit 1;
    }
  }
  
  return ref public;
}

test_octopussy := function (server="./test_glish",options="")
{
  oct := octopussy(server=server,options=options);
  if( is_fail(oct) || !oct.connected() )
    fail 'unable to connect to server';
  oct.subscribe("Pong");
  # create a ping message
  run := T;
  count := 0;
  while( run && count<5 )
  {
    rec := [=];
    rec.Timestamp := 0;
    rec.Invert := T;
    rec.Data := random(10);
    rec.Data_B := [];
    rec.Count := count;
    count +:= 1;
    res := oct.publish("Ping",rec);
    if( is_fail(res) )
      print "publish failed",res;
    msg := oct.receive();
    if( is_fail(msg) )
    {
      print "Receive failed: ",msg;
      run := F;
    }
    else
    {
      print "Received: ",msg;
    }
  }
}

#test_octopussy();
#exit 0;
