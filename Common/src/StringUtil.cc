//#  StringUtil.cc: implementation of the string utilities class.
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include <Common/StringUtil.h>
#include <iostream>
#include <stdarg.h>

namespace LOFAR
{
  
  using std::string;
  using std::vector;

  std::vector<std::string> StringUtil::split(const std::string& s, char c)
  {
    vector<string> v;
    string::size_type i, j;
    i = j = 0;
    while (j != string::npos) {
      j = s.find(c,i);
      if (j == string::npos) v.push_back(s.substr(i));
      else v.push_back(s.substr(i,j-i));
      i = j+1;
    }
    return v;
  }

//
// formatString(format, ...) --> string
//
// Define a global function the accepts printf like arguments and returns a string.
//
const std::string formatString(const	char* format, ...) {
	char		tmp_cstring[10240];
	va_list		ap;

	va_start (ap, format);
	vsnprintf(tmp_cstring, sizeof(tmp_cstring), format, ap);
	va_end   (ap);

	return   std::string(tmp_cstring);
}

//
// timeString(aTime [,format]) --> string
//
// Define a global function that convert a timestamp into a humanreadable format.
//
const std::string timeString(time_t		aTime, 
							 bool		gmt,
							 char* 		format)
{
	char	theTimeString [256];
	strftime(theTimeString, 256, format, gmt ? gmtime(&aTime) : localtime(&aTime));

	return (theTimeString);
}

} // namespace LOFAR
