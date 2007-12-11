from Timba.TDL import *
from Timba.Meq import meq
from Timba import pynode
import pyfits

import Meow
import math
import os
from Timba import mequtils

import DigestifBeam

Settings.forest_state.cache_policy = 100;

TDLCompileOption("beam_filename","Filename of beam pattern",
                  TDLFileSelect("*.beam",default="digestif.beam",exist=True));

ARCMIN = math.pi/(180*60);

def _define_forest (ns,**kwargs):
  ns.beam << Meq.PyNode(class_name="DigestifBeamReaderNode",module_name="DigestifBeam",
                        file_name=beam_filename);
  Meow.Bookmarks.Page("Phased beam").add(ns.beam);

def _tdl_job_load_beam (mqs,parent,**kwargs):
  from Timba.Meq import meq
  gridding = DigestifBeam.read_beam_gridding(beam_filename);
  cells = gridding.compute_cells();
  request = meq.request(cells,rqtype='ev');
  mqs.execute('beam',request);
