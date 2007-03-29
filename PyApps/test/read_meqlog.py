#!/usr/bin/python
from Timba import dmi
from Timba import mequtils

boio = mequtils.open_boio("meqlog.mql");

while True:
  entry = mequtils.read_boio(boio);
  if entry is None:
    break;
  for key,val in entry.iteritems():
    if isinstance(val,dmi.record):
      print key,"record";
    else:
      print key,val;
