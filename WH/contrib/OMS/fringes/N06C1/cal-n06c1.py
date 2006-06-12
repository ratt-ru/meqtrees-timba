from Timba.TDL import *

# import settings for tree below, so we can modify them
from Timba.Contrib.OMS.Calibration import fringe_fit_settings

fringe_fit_settings.num_stations = 10;
fringe_fit_settings.field_list = range(4);
fringe_fit_settings.ddid_list = range(4);


# import standard fringe-fitter trees and jobs
from Timba.Contrib.OMS.Calibration.fringe_fit import *


Settings.forest_state.cache_policy = 100;  # -1 for minimal, 1 for smart caching, 100 for full caching

# setup some bookmarks
from Timba.Contrib.OMS import Bookmarks

Settings.forest_state.bookmarks = [
  record(name='Predicted visibilities',page=Bookmarks.PlotPage(
      ["visibility:all:G:1:2","spigot:1:2","residual:1:2"],
      ["visibility:all:G:1:7","spigot:1:7","residual:1:7"],
      ["visibility:all:G:2:7","spigot:2:7","residual:2:7"]
  )), 
  record(name='Corrected visibilities',page=Bookmarks.PlotPage(
      ["corrected:1:2","corrected:1:7"],
      ["corrected:2:7"]
  )), 
  record(name='Source solutions',page=Bookmarks.PlotPage(
      ["I:cs","Q:cs","U:cs"],
      ["V:cs","sigma1:cs","sigma2:cs"],
      ["phi:cs","solver"]
  )),
  record(name='Flux and phase solutions',page=Bookmarks.PlotPage(
      ["I:3C345","phase:L:1"],
      ["phase:L:2","phase:L:7"],
      ["solver"]
  )),
  record(name='Baseline phase solutions',page=Bookmarks.PlotPage(
      ['phase:LL:1:2','phase:time:LL:1:2','obs_phase:time:LL:1:2'],
      ['phase:LL:1:4','phase:time:LL:1:4','obs_phase:time:LL:1:4'],
      ['phase:LL:1:7','phase:time:LL:1:7','obs_phase:time:LL:1:7'],
  )),
  record(name='Gain solutions',page=Bookmarks.PlotPage(
      ['gain:R:1','gain:R:2'],
      ['gain:R:7','gain:L:1'],
      ['gain:L:2','gain:L:7']
  )),
];



# standard clause for stand-alone testing
if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
