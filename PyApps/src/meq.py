#!/usr/bin/python

from dmitypes import *

def node(classname,name,children=None,groups=None,**kwargs):
  defrec = srecord({'class':classname},name=name,**kwargs);
  if children:
    if not isinstance(children,(list,tuple)):
      children = (children,);
    defrec.children = children;
  if groups:
    defrec.node_groups = map(make_hiid,groups);
  return defrec;

