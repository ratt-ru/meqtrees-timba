# file: ../JEN/demo/CollatedHelpRecord.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 03 jun 2008: creation (from QuickRef.py)
#   - 01 jul 2008: implemented .orphans()
#   - 16 jul 2008: format_html()
#
# Remarks:
#
# Description:
#


 
#********************************************************************************
# Initialisation:
#********************************************************************************

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq

#=================================================================================

class CollatedHelpRecord (object):
   """
   This object collects and handles a hierarchical set of help strings
   in a record. This is controlled by the path, e.g. 'QuickRef.MeqNodes.unops'.
   """

   def __init__(self, name='CollatedHelpRecord', chrec=None):
      self._name = name 
      self.clear()
      if isinstance(chrec, record):
          self._chrec = chrec
      return None

   def clear (self):
      self._chrec = record(help=None, order=[])
      self._folder = record()
      self._orphans = []
      self._nodestub = None
      self.path(init='CollatedHelpRecord') 
      return None

   def chrec (self):
      return self._chrec

   def nodestubname (self, trace=False):
      """
      Derive a nodestub name from the current path.
      """
      return self.path2name (n=2, trace=trace)

   def path2name (self, n=None, trace=False):
      """
      Derive a name from n last sections of the current path.
      """
      ss = self._path.split('.')
      if isinstance(n,int) and n>0:
         ss1 = ss[-min(len(ss),n):]
      else:
         ss1 = ss
      name = ss1[0]
      if len(ss1)>1:
         for s in ss1[1:]:
            name += '_'+s
      if trace:
         print '** nodestubname():',ss,ss1,'->',name
      return name

   #-------------------------------------------------------------------------------

   def path (self, append=None, up=False, temp=None,
             init=False, trace=False):
      """
      Helper function to get/manipulate the path to a specific item.
      - If init is a string, set self._path 
      - If append is a string, append it to self._path (with '.')
      - If up=True, remove the last appended item
      - If temp is string, same as append, but self._path unaffected
      The path string controls many of the functions in this object.
      NB: This function is called from all QR_... modules!
      """
      if isinstance(init,str):
         self._path = init

      if isinstance(temp,str):
         # Return a temporary path (does NOT affect self._path)
         path = self._path+'.'+str(temp)
         if trace:
            print '\n** rider.path(temp=',temp,') ->',path
         return path

      elif isinstance(append,str):
         # Extend the path string, separated by '.'
         self._path += '.'+str(append)

      elif up:
         # Go up one level, by removing the last append:
         ss = self._path.split('.')
         last = '.'+ss[len(ss)-1]
         self._path = self._path.replace(last,'')

      # Return the current self._path (except if temp=str):
      if trace:
            print '\n** rider.path(',append,up,init,') ->',self._path
      return self._path

   #---------------------------------------------------------------------

   def insert_help (self, path=None, help=None, append=True,
                    rr=None, level=0, trace=False):
      """
      Insert a help-item at the designated (path) position (recursive)
      """
      if level==0:
         rr = self._chrec

      if isinstance(path,str):
         path = path.split('.')

      key = path[0]
      if not rr.has_key(key):
         rr.order.append(key)
         rr[key] = record(help='')
         # if len(path)>1:
         rr[key].order = []

      if len(path)>1:                        # recursive
         self.insert_help(path=path[1:], help=help, rr=rr[key],
                          append=append, level=level+1, trace=trace)

      else:
         if append:
            rr[key].help += help 
         else:
            rr[key].help = help 
         if trace:
            prefix = self.prefix(level)
            print '.insert_help(append=',append,'):',prefix,key,':',help
      # Finished:
      return None

   #---------------------------------------------------------------------

   def show(self, txt=None, rr=None, full=False, key=None, level=0):
      """
      Show the internal record (recursive)
      """
      if level==0:
         print '\n** CHR.show(',txt,', full='+str(full),'):',str(self._name)
         rr = self._chrec
      prefix = self.prefix(level)

      if not rr.has_key('order'):                # has no 'order' key
         for key in rr.keys():
            if isinstance(rr[key], (list,tuple)):
               if len(rr[key])>1:
                  print prefix,key,':',rr[key][0]
                  for s in rr[key][1:]:
                     print prefix,len(key)*' ',s
               else:
                  print prefix,key,':',rr[key]
            else:
               print prefix,key,'(no order):',type(rr[key])

      else:                                      # has 'order' key
         for key in rr.keys():
            if isinstance(rr[key], (list,tuple)):
               if key in ['order']:              # ignore 'order'
                  if full:
                     print prefix,key,':',rr[key]
               elif len(rr[key])>1:
                  print prefix,key,':',rr[key][0]
                  for s in rr[key][1:]:
                     print prefix,len(key)*' ',s
               else:
                  print prefix,key,'(',len(rr[key]),'):',rr[key]
            elif not isinstance(rr[key], (dict,Timba.dmi.record)):
               print prefix,key,'(',type(rr[key]),'??):',rr[key]
               
         for key in rr['order']:
            if isinstance(rr[key], (dict,Timba.dmi.record)):
               self.show(rr=rr[key], key=key, level=level+1, full=full) 
            else:
               print prefix,key,'(',type(rr[key]),'??):',rr[key]

      if level==0:
         print '**\n'
      return None


   #---------------------------------------------------------------------

   def format(self, rr=None, ss=None, key=None,
              path=None, level=0, trace=False):
      """
      Recursively format a help-string (below path), to be printed.
      """
      if level==0:
         ss = '\n'
         if path:
            rr = self.subrec(path, chrec=True, trace=False)
         else:
            rr = self._chrec
         if trace:
            print '\n** Start of .format():'
            
      prefix = '\n'+self.prefix(level)

      # First attach the overall help, if available:
      if rr.has_key('help'):
         help = rr['help']
         if isinstance(help, str):
            ss += prefix+str(help)
         elif isinstance(help, (list,tuple)):
            ss += prefix+str(help[0])
            if len(help)>1:
               # s1 = str(len(str(key))*' ')           # keys too long...
               s1 = str(5*' ')                        # <---- !!
               for s in help[1:]:
                  ss += prefix+s1+str(s)

      # Then recurse in the proper order, if possible:
      keys = rr.keys()
      if rr.has_key('order'):                # has no 'order' key
         keys = rr['order']
      for key in keys:
         if isinstance(rr[key], (dict,Timba.dmi.record)):
            ss = self.format(rr=rr[key], ss=ss, key=key,
                             level=level+1, trace=trace) 
      # Finished:
      if len(keys)>1:
         ss += prefix
      if level==0:
         ss += '**\n'
         if trace:
            print '\n** End of .format():\n'
            print ss
      return ss


   #---------------------------------------------------------------------
   
   def prefix (self, level=0):
      """Indentation string"""
      ps= ' '+(level*'..')+' '
      # ps= ' '+str(level)+(level*'..')+' '
      return ps

   #---------------------------------------------------------------------
   
   def tag (self, level=0):
      """Indentation string"""
      ps= ' '+(level*'..')+' '
      # ps= ' '+str(level)+(level*'..')+' '
      return ps

#    def helpAbout(self):
#      tmp_str="<font color=\"blue\">LSM Browser</font><br/>"
#      tmp_str+="<p>For more information please visit Timba MeqWiki Page at<br/>"
#      tmp_str+="<span style=\"font-style: italic;\">http://lofar9.astron.nl/meqwiki/</span><br>"
#      tmp_str+="</p>"
#      dialog=SDialog(self)
#      dialog.setInfoText(tmp_str)
#      dialog.setTitle("Help")
#      dialog.show()


   #---------------------------------------------------------------------

   def topic_name(self, path=None, trace=False):
       """
       Use the path string to make a topic (bundle) name,
       to be used for the header and for bundle node-name etc.
       Called from QuickRefUtil.py, and from topic_header() below.
       The name of the bundle (node, page, folder) is the last
       part of the path string, i.e. after the last dot ('.')
       """
       if path==None:
          path = self.path()
       ss = path.split('.')
       nss = len(ss)
       name = ss[nss-1]
       return name

   #---------------------------------------------------------------------

   def topic_header(self, path=None, mode='html', trace=False):
       """
       Use the path string to make a QuickRef topic header.
       Called from QuickRefUtil.py (also with mode=='prefix')
       """
       # The name of the bundle (node, page, folder) is the last
       # part of the path string, i.e. after the last dot ('.')
       if path==None:
          path = self.path()
       ss = path.split('.')
       nss = len(ss)
       name = ss[nss-1]
       # name = self.topic_name (path)

       # Prepend a header:
       level = nss-2
       qhead = ''
       if mode=='html':
          qhead += '<h'+str(level+2)+'>\n '   # html tag (see CollatedHelpRecord())
          qhead += '('+str(level+2)+')  '

       if level==0:                           # i.e. nss=2
          qhead += 'MODULE: '+ss[nss-2]+'_'+ss[nss-1]
       elif level==1:                         # i.e. nss=3
          qhead += 'TOPIC: '+ss[nss-2]+'_'+ss[nss-1]
       elif level==2:                         # i.e. nss=4
          qhead += 'sub-TOPIC: '+ss[nss-3]+'_'+ss[nss-2]+'_'+ss[nss-1]
       elif level==3:                         # i.e. nss=5
          qhead += 'sub-sub-TOPIC: '+ss[nss-3]+'_'+ss[nss-2]+'_'+ss[nss-1]
       elif level>3:
          qhead += 'sub-sub-sub-...: '+ss[nss-3]+'_'+ss[nss-2]+'_'+ss[nss-1]

       if mode=='html':
          qhead += ' </h'+str(level+2)+'>'    # closing html tag

       if mode=='prefix':                     # used for node-names
          qhead = qhead.split(':')[0]
          qhead += '__'
          if level<1: qhead = ''

       if trace:
          print '\n** topic_header(',path,mode,'):\n    ->',qhead,'\n'
       return qhead

   #---------------------------------------------------------------------

   def html_style (self):
      """
      <!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
      <html>
      <head>
      <meta content=\"text/html; charset=UTF-8\" http-equiv=\"content-type\">
      <meta name=\"AUTHOR\" content=\"\">
      <meta name=\"keywords\" content=\"\">
      <title>Title</title>
      <style type=\"text/css\">
      body {color: black; background: white; font-size: 11px; }
      body, div, p, th, td, li, dd {font-family: Verdana Lucida, Arial, Helvetica, sans-serif; }
      </style>
      </head>
      """
      return self.html_style.__doc__


   # NOT recommended:
   # h0 {color: yellow;}
   # h1 {color: red;}
   # h2 {color: magenta;}
   # h3 {color: green;}
   # h4 {color: blue;}
   # h5 {color: blue;}

   #---------------------------------------------------------------------

   def format_html(self, rr=None, ss=None, key=None,
                   path=None, level=0, trace=False):
      """
      Recursively format an html help-string (below path).
      """
      if level==0:
         ss = self.html_style()
         if path:
            rr = self.subrec(path, chrec=True, trace=False)
         else:
            rr = self._chrec
         if trace:
            print '\n** Start of .format_html():'
            
      prefix = '\n'+self.prefix(level)

      # First attach the overall help, if available:
      if rr.has_key('help'):
         help = rr['help']
         if isinstance(help, str):
            ss += str(help)
            ss += '<br/>'
         elif isinstance(help, (list,tuple)):
            for i,s in enumerate(help):
               if len(s)==0:
                  ss += '\n<br/>'
               else:
                  ss += '\n'+str(s)
                  if '<li>' in s:
                     pass
                  elif '<ul>' in s or '</ul>' in s:
                     pass
                  elif s[0]=='<':
                     pass
                  elif s[len(s)-1]=='>':
                     pass
                  else:
                     ss += '<br/>'

      # Then recurse in the proper order, if possible:
      keys = rr.keys()
      if rr.has_key('order'):                # has no 'order' key
         keys = rr['order']
      for key in keys:
         if isinstance(rr[key], (dict,Timba.dmi.record)):
            ss = self.format_html(rr=rr[key], ss=ss, key=key,
                                  level=level+1, trace=trace) 
      # Finished:
      if len(keys)>1:
         # ss += prefix
         pass
      if level==0:
         ss += '\n</html>'
         if trace:
            print '\n** End of .format_html():\n'
            print ss
      return ss


   #---------------------------------------------------------------------

   def save_html (self, filename='CollatedHelpString',
                  path=None, external=None):
      """
      Save something in the specified file (with extension .html).
      If 'external' is a string, save that.
      Otherwise, save the formatted internal string (from path). 
      """
      if isinstance(external, str):
         ss = external
      else:
         ss = self.format_html(path=path)
      filename = filename.split('.')[0] + '.html'
      file = open (filename,'w')
      file.writelines(ss)
      file.close()
      if isinstance(external, str):
         print '\n** Saved user-defined string in file: ',filename,'**\n'
      else:
         print '\n** Saved the help string (from path=',path,') in file: ',filename,'**\n'
      return filename


   #---------------------------------------------------------------------

   def save (self, filename='CollatedHelpString',
             path=None, external=None):
      """
      Save something in the specified file (default extension .meqdoc).
      If 'external' is a string, save that.
      Otherwise, save the formatted internal string (from path). 
      """
      if isinstance(external, str):
         ss = external
      else:
         ss = self.format(path=path)
      if not '.' in filename:
         filename += '.meqdoc'
      file = open (filename,'w')
      file.writelines(ss)
      file.close()
      if isinstance(external, str):
         print '\n** Saved user-defined string in file: ',filename,'**\n'
      else:
         print '\n** Saved the help string (from path=',path,') in file: ',filename,'**\n'
      return filename
      

   #---------------------------------------------------------------------

   def subrec(self, path, chrec=False, trace=False):
      """
      Extract (a deep copy of) the specified (path) subrecord
      from the internal self._chrec.
      If chrec==True, just return the 'naked' record.
      Otherwise, return a new CHR object.
      """
      if trace:
         print '\n** .extract(',path,'):'

      rr = copy.deepcopy(self._chrec)
      ss = path.split('.')
      for key in ss:
         if trace:
            print '-',key,ss,rr.keys()
         if not rr.has_key(key):
            s = '** key='+key+' not found in: '+str(ss)
            raise ValueError,s
         else:
            rr = rr[key]

      # Optional: return the 'naked' record: 
      if chrec:
         return rr
      
      # Return another object of the same type:
      newname = 'subrec('+path+')'
      result = CollatedHelpRecord(newname, chrec=rr)
      if trace:
         result.show(txt=path)
      return result
      
   #---------------------------------------------------------------------

   def cleanup (self, rr=None, level=0, trace=False):
      """
      Return a cleaned-up copy of its internal record.
      """
      if level==0:
         if trace:
            print '\n** .cleanup():'
         rr = copy.deepcopy(self._chrec)
            
      if isinstance(rr, dict):
         if rr.has_key('order'):
            rr.__delitem__('order')                   # remove the order field
            for key in rr.keys():
               if isinstance(rr[key], dict):          # recursive
                  rr[key] = self.cleanup(rr=rr[key], level=level+1)

      if level>0:
          # Not finished: Return to former level:
          return rr

      # Finished: eturn another object of the same type:
      newname = 'upcleaned'
      result = CollatedHelpRecord(newname, chrec=rr)
      if trace:
          print '** finished .cleanup()'
      return result


   #---------------------------------------------------------------------

   def bookmark (self, path, trace=False):
      """
      A little service to determine [page,folder] from path.
      It is part of this CHR class because it initializes each time.
      This is necessary to avoid extra pages/folders.
      """
      # trace = True
      
      ss = path.split('.')
      nss = len(ss)

      page = None
      page = ss[nss-1]                          # the last one, always there
      if nss>1:
         page = ss[nss-2]+'_'+ss[nss-1]

      folder = None
      if len(ss)>3:
         folder = ss[nss-3]+'_'+ss[nss-2]       # same format as page above (essential!)

      if folder:
         self._folder.setdefault(folder,0)
         self._folder[folder] += 1
      elif page and self._folder.has_key(page):
         folder = page                          # works well for ...resampling_modres....
         self._folder[folder] += 1              # ....?
         # page = None                            # produces 'autopage' pages in the folder
         # page = '..dummy..'                     # still there, clean up later

      # Finished:
      if trace:
         print '*** CHR.bookmark():',len(ss),ss,' page=',page,' folder=',folder
      return [page,folder]

   #---------------------------------------------------------------------

   def orphans (self, node=None, clear=False, trace=False):
      """
      Add the given node(s) to the internal orphans list.
      If no node(s) supplied, just return the internal list.
      This is an example of the CHR rider being used as a holder
      of items that need to be held for some reason.
      """
      # trace = True
      s = '** CHR.orphans('+str(type(node))+', clear='+str(clear)+'): '
      if clear:
         self._orphans = []

      if is_node(node):
         s += ' node='+str(node)
         self._orphans.append(node)
      elif isinstance(node,(list,tuple)):
         s += ' n='+str(len(node))
         if len(node)>0:
            s += ' node[0]='+str(node[0])
         self._orphans.extend(node)

      if trace:
         print '\n'+s+' (total='+str(len(self._orphans))+')'
      return self._orphans


   #---------------------------------------------------------------------

   def countag (self, tag=None, action=None, 
                init=False, txt=None, trace=False):
      """Helper function for .check_html_tags()"""
      if init:
         self._countag = dict()
      if isinstance(tag,str):
         self._countag.setdefault(tag, 0)
         if action=='up':
            self._countag[tag] += 1
         elif action=='down':
            self._countag[tag] -= 1
         elif action=='reset':
            self._countag[tag] = 0
         return self._countag[tag]
      return self._countag

   #---------------------------------------------------------------------

   def indent (self, ss=None, add=0, revert=False, reset=False, trace=False):
      """Helper function for .check_html_tags(), to control indentation"""
      # trace = True

      # Modify the indentation level, if required:
      if reset:
         self._indents = [0]
         self._indent = self._indents[0]          # i.e. zero
         self._tempindent = 0
         self._last_was_comma = False             # just in case (harmless kludge)
      if isinstance(ss,int):                      # set specific indentation 
         # self._indents = [0]                      # ...reset....?
         if ss>0:
            self._indents.append(ss)
         self._indent = self._indents[-1]         # set to the last one
         self._tempindent = 0
      if add:                                     # 'increase' indentation
         self._indent += add                      # may be negative
         self._indents.append(self._indent)
         self._tempindent += 1 
      if revert:
         if len(self._indents)>1:                 # just in case
            self._indents = self._indents[:-1]    # remove the last one
            self._indent = self._indents[-1]      # set to the new last one
         self._tempindent -= 1 
      self._indent = max(self._indent,0)

      if trace:
         print '** .indent(',ss,add,revert,reset,'): ',self._indents,self._tempindent,self._indent

      if not isinstance(ss,str):                  # not a string
         ss = self._indent                        # return current indentation 
      else:                                       # Indent the given string:
         if self._indent>0:
            prefix = '<font color="white">'+str(self._indent*'.')+'</font>'
            # prefix = '('+str(self._indent)+')'+prefix      # testing only
            ss = prefix + ss
            if trace:
               print '    ',ss
      
      return ss

   #---------------------------------------------------------------------

   def replace_html_chars (self, help, trace=False):
      """Replace characters that cause problems with html
      with their escape versions."""
      if not isinstance(help,str):                       # e.g. None
         return help
      ss = help
      ss = ss.replace('<<',' &lt &lt &#32')              # escape char &lt = <  
      # ... to be elaborated ...
      return ss

   #---------------------------------------------------------------------

   def check_html_tags(self, help, include_style=False, trace=False):
      """
      Check for the presence and integrity of a minimum of html tags
      in the given string (help).
      If include_style==True, include the QuickRef html style file.
      """
      # print '\n',help,'\n'
      if not isinstance(help,str):
         help = ''

      # First replace some substrings that might mess up the html: 
      ss = self.replace_html_chars (help, trace=False)

      # Split in lines, i.e. on the '\n' chars from a triple-quoted string:
      ss = ss.split('\n')

      # Look for specific features in the lines:
      self.countag(init=True)
      self.indent(reset=True)
      self._last_was_comma = False 
      for i,s in enumerate(ss):
         if trace:
            print '-',i,':',ss[i]

         # if self.countag('function_call')>0:
         #    self.countag('function_call','up') # 

         if self.countag('code_lines')>0:
            fline = self.countag('function_code')   # special case
            if fline>0:
               if fline==1:                         # 1st line (function call)
                  pass
               elif fline==2:                       # 2nd line: increase indentation
                  self.indent(add=10)
               self.countag('function_code','up')   # count the lines of function code

            ss[i] = self.indent(s)                 # FIRST indent the line
            ss[i] += '<br>'
            # Change the FUTURE indentation, if required:
            s1 = s.strip()                         # remove leading and trailing blanks
            if len(s1)>0:
               if s1[-1]==',':                     # last char is a comma
                  if not self._last_was_comma:
                     ## nindent = self._indent + len(s1.split('(')[0])
                     self.indent(add=15)           # set indentation
                  self._last_was_comma = True 
               elif s1[-1]==')':                   # last char is a closing bracket
                  if self._last_was_comma: 
                     self.indent(revert=True)      # revert to earlier indentation
                  self._last_was_comma = False 
            self.countag('code_lines','up')        # count the code lines

         #................................................................................

         if ss[i] in ['',' ','  ','   ','    ']:      # blank line
            ss[i] = ''
            if self.countag('ul')>0:
               self.countag('ul','down')
               ss[i] += '</ul>\n'
            ss[i] += '<p>'

         elif '<ul>' in ss[i]:              # start of unordered list
            self.countag('ul','up')
         elif '</ul>' in ss[i]:             # end of unordered list
            self.countag('ul','down')
         elif '<li>' in ss[i]:              # list element (assume unordered list)
            aa = ss[i].split(':')
            if len(aa)>1:
               ss[i] = aa[0]+':'
               # ss[i] = '<em>'+aa[0]+':</em>'                             # NB: forces a line-break...!
               # ss[i] = '<font color="blue">' + aa[0] + ':' + '</font>'   # NB: forces a line-break...!
               for k,a in enumerate(aa):
                  if k>0: ss[i] += a
            if self.countag('ul')==0:
               ss[i] = '<ul>\n'+ss[i]
               self.countag('ul','up')

         elif '<function_code>' in ss[i]:
            self.countag('function_code','up')
            self.countag('code_lines','up')
            self.indent(5)       
            ss[i] = '\n<br><font color="blue">'
         elif '</function_code>' in ss[i]:
            self.countag('function_code','reset')
            self.countag('code_lines','reset')
            self.indent(0)
            ss[i] = '</font><br>\n'

         elif '<code_lines>' in ss[i]:
            self.countag('code_lines','up')
            self.indent(15)       
            ss[i] = '<br>\n'
            ss[i] += '<font color="red">\n'
         elif '</code_lines>' in ss[i]:
            self.countag('code_lines','reset')
            self.indent(0)
            ss[i] = '<br>\n'
            ss[i] += '</font>'

         elif '<warning>' in ss[i]:
            self.countag('warning','up')
            ss[i] += '<font color="magenta"> Warning: '
         elif '</warning>' in ss[i]:
            self.countag('warning','reset')
            ss[i] += '</font>\n'

         elif '<error>' in ss[i]:
            self.countag('error','up')
            ss[i] += '<font color="red"> Error: '
         elif '</error>' in ss[i]:
            self.countag('error','reset')
            ss[i] += '</font>\n'

         elif '<remark>' in ss[i]:
            self.countag('remark','up')
            ss[i] += '<font color="green"> NB: '
         elif '</remark>' in ss[i]:
            self.countag('remark','reset')
            ss[i] += '</font>\n'

         elif '<tip>' in ss[i]:
            self.countag('tip','up')
            ss[i] += '<i><b> Tip: </b>'
         elif '</tip>' in ss[i]:
            self.countag('tip','reset')
            ss[i] += '</i>\n'

      # Clean up:
      for i in range(self.countag('ul')):
         ss.append('</ul>')
                
      # Reassemble a single string, with line-breaks:
      ssout = ''
      if include_style:
         ssout = self.html_style()
      for s in ss:
         ssout += '\n'+s

      if trace:
         print ssout
      return ssout
                




#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: CollatedHelpRecord.py:\n' 
   from Timba.TDL import *
   from Timba.Meq import meq
   ns = NodeScope()

   if 1:
      rider = CollatedHelpRecord()


   if 1:
      rider.indent(reset=True, trace=True)
      rider.indent(10, trace=True)
      rider.indent(add=10, trace=True)
      rider.indent(revert=True, trace=True)
      rider.indent('text', trace=True)
      rider.indent(0, trace=True)
      rider.indent('text', trace=True)

   if 0:
      rider.path(trace=True)
      rider.path(init='test', trace=True)
      rider.path(append='module', trace=True)
      rider.path(append='topic', trace=True)
      rider.path(append='subtopic', trace=True)
      rider.nodestubname(trace=True)
      rider.path(up=True, trace=True)
      rider.path(up=True, trace=True)
      rider.path(temp='temp1', trace=True)
      rider.path(temp='temp2', trace=True)
      rider.path(trace=True)
      rider.nodestubname(trace=True)

 
   if 0:
      cc = rider.orphans(ns << 1.2, trace=True)
      cc = rider.orphans(ns << 1.2, trace=True)
      cc = rider.orphans(trace=True)
      print cc
      cc = rider.orphans(clear=True, trace=True)

   if 0:
      path = 'aa.bb.cc.dd'
      help = 'xxx'
      rider.insert_help(path=path, help=help, trace=True)

   if 0:
      import QR_MeqNodes
      QR_MeqNodes.MeqNodes(ns, 'test', rider=rider)
      # rider.show('testing', full=True)
      # print rider.format()

      if 1:
         path = 'test.MeqNodes.binops'
         # path = 'test.MeqNodes'
         sub = rider.subrec(path, trace=True)
         sub.show(full=False)
         sub.show(full=True)
         sub.format(trace=True)

         if 0:
            clean = sub.cleanup(trace=True)
            # The order fields should now have disappeared: (no order)
            clean.show(full=True)
            # Finally, test whether the original self._chrec still has order fields:
            sub.show('after cleanup', full=True)
            
   print '\n** End of standalone test of: CollatedHelpRecord.py:\n' 

#=====================================================================================



