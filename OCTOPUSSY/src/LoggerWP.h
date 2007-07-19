//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#ifndef OCTOPUSSY_LoggerWP_h
#define OCTOPUSSY_LoggerWP_h 1

#include <OCTOPUSSY/WorkProcess.h>
    
namespace Octopussy
{

#pragma aid LoggerWP Max Level Scope

//##ModelId=3CA044DE02AB
class LoggerWP : public WorkProcess
{
  public:
      static int registerApp ();
      static WPRef constructor (DMI::Record::Ref &initrecord);
      
      //##ModelId=3CA0451401B9
      LoggerWP (int maxlev = 9999, int scope = Message::GLOBAL);

    //##ModelId=3DB9369A0073
      ~LoggerWP();


      //##ModelId=3CA045020054
      virtual void init ();

      //##ModelId=3CA05A7E01CE
      virtual void stop ();

      //##ModelId=3CA0450C0103
      virtual int receive (Message::Ref &mref);

      //##ModelId=3CA04AF50212
      void setScope (int scope);

      //##ModelId=3CA04A1F03D7
      virtual void logMessage (const string &source, const string &msg, int level, AtomicID type);

    //##ModelId=3DB9369A018C
      int level () const;
    //##ModelId=3DB9369A01F0
      void setLevel (int value);

    //##ModelId=3DB9369A02B8
      int consoleLevel () const;
    //##ModelId=3DB9369A0330
      void setConsoleLevel (int value);

  private:
    //##ModelId=3DB9369B0043
      LoggerWP(const LoggerWP &right);

    //##ModelId=3DB9369B016F
      LoggerWP & operator=(const LoggerWP &right);

  private:
    // Data Members for Class Attributes

      //##ModelId=3CA048E90395
      int level_;

      //##ModelId=3CA052560312
      int consoleLevel_;

    // Additional Implementation Declarations
    //##ModelId=3DB9369902DF
      int scope_;
      
    //##ModelId=3DB936990361
      string filename_;
    //##ModelId=3DB9369903CF
      int fd;
};

// Class LoggerWP 

//##ModelId=3DB9369A018C
inline int LoggerWP::level () const
{
  return level_;
}

//##ModelId=3DB9369A01F0
inline void LoggerWP::setLevel (int value)
{
  level_ = value;
}

//##ModelId=3DB9369A02B8
inline int LoggerWP::consoleLevel () const
{
  return consoleLevel_;
}

//##ModelId=3DB9369A0330
inline void LoggerWP::setConsoleLevel (int value)
{
  consoleLevel_ = value;
}


};
#endif
