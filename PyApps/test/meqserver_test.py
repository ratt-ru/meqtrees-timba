#!/usr/bin/python

import meq
import meqserver
import time
import octopussy

def stress_test (n=10000,verbose=0,**kwargs):
  mqs = meqserver.default_mqs(verbose=verbose,**kwargs);

  mqs.set_debug('MeqNode',0);
  mqs.set_debug('MeqForest',0);
  mqs.set_debug('MeqSink',0);
  mqs.set_debug('MeqSpigot',0);
  mqs.set_debug('MeqVisHandler',0);
  mqs.set_debug('MeqServer',0);
  mqs.set_debug('meqserver',0);
  # create record for small subtree
  rec = meq.node('MeqAdd','root',children=(
          meq.node('MeqAdd','a',children=meq.node('MeqConstant','const',value=0)),
          meq.node('MeqAdd','b',children="c"),
          meq.node('MeqAdd','c',children="c"),
          meq.node('MeqAdd','d',children="c") ));
          
  mqs._pprint.pprint(rec);
          
  for i in range(n):
    if verbose:
      print 'Creating tree ',i;
    si = str(i);
    rec.name = 'root'+si;
    rec.children[0].name = 'a'+si;
    rec.children[1].name = 'b'+si;
    rec.children[2].name = 'c'+si;
    rec.children[3].name = 'd'+si;
    cn = 'const'+si;
    rec.children[0].children[0].name = cn;
    rec.children[1].children = cn;
    rec.children[2].children = cn;
    rec.children[3].children = cn;
    mqs.createnode(rec,silent=True);
    
  print 'getting node list';
  t1 = time.time();
  nodelist = mqs.getnodelist();
  t1 = time.time() - t1;
  print nodelist;
  print 'got it in',t1,'seconds';
 
if __name__ == '__main__':
  stress_test(1000,verbose=1,spawn=True,launch=False,wp_verbose=0);

  meqserver.mqs.event_loop();  
  meqserver.mqs.halt();
  octopussy.stop();
