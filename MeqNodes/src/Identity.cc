//# Identity.cc: Selects result planes from a result set
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#include <MeqNodes/Identity.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Request.h>

namespace Meq {    

//##ModelId=400E5355022C
Identity::Identity()
    : Node(1) // exactly 1 child expected
{}

//##ModelId=400E5355022D
Identity::~Identity()
{}

//##ModelId=400E53550237
int Identity::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childref,
                         const Request &request,bool)
{
  resref = childref[0];
  return 0;
}
} // namespace Meq
