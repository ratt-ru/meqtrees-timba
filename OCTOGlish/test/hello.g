include "../../../src/Glish/octopussy.g"

test_hello := function (server="./octoglish",options="")
{
  oct := octopussy(server=server,options=options);
  if( is_fail(oct) || !oct.connected() )
    fail 'unable to connect to server';

  # setup initial subscriptions
#  oct.subscribe("GW.Remote.Up.*");
  oct.subscribe("IMTestWP.HelloWorld.*");
  oct.subscribe("WP.Hello.IMTestWP.*");
  
  # start the system
  oct.start();
 
  # create a ping message
  run := T;
  count := 0;
  while( run && count<5 )
  {
#    rec := [=];
#    rec.Timestamp := 0;
#    rec.Invert := T;
#    rec.Data := random(10);
#    rec.Count := count;
#    count +:= 1;
#    res := oct.publish("Ping",rec);
#    if( is_fail(res) )
#      print "publish failed",res;

    print "waiting...";
    msg := oct.receive();
    if( is_fail(msg) )
    {
      print "Receive failed: ",msg;
      run := F;
    }
    else
    {
      print "Received: ",msg;
      print "id:", msg::id;
      print "to:", msg::to;
      print "from:", msg::from;
      print "priority", msg::priority;
      print "state", msg::state;

      if (msg::from !~ m/^GlishClientWP/)
      {
      # remember to use single quotes -- double quotes imply a string array
	msg["Content"] := 'from glish';
        res := oct.publish("IMTestWP.HelloWorld",msg);
        if( is_fail(res) ) print "publish failed",res;
      }
      if (msg::id ~ m/WP.Hello.IMTestWP/)
      {
	  res := oct.publish("start");
	  if (is_fail(res)) print "publish failed", res
      }
    }
  }
}
