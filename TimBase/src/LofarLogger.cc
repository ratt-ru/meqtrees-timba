//#  LofarLogger.cc: Interface to the log4cplus logging package
//#
//#  Copyright (C) 2004
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

//# Includes
#include <stdio.h>					// snprintf
#include <unistd.h>					// readlink
#include <libgen.h>				// basename
#include <Common/LofarLogger.h>

namespace LOFAR {

//#------------------------- Internal implementation -----------------------------
//
// lofarLoggerInitNode()
//
// Creates a NDC with the text "application@node" and pushes it
// on the NDC stack
void lofarLoggerInitNode(void) {
	int		MAXLEN = 128;
	int		applNameLen = 0;
	char	hostName [MAXLEN];
	char	applName [MAXLEN];
	char	loggerId [MAXLEN];

	// try to resolve the hostname
	if (gethostname (hostName, MAXLEN-1) < 0) {
		hostName[0]='\0';
	}

	// try to resolve the applicationname
	applNameLen = readlink("/proc/self/exe", applName, MAXLEN-1);
	if (applNameLen >= 0)
		applName[applNameLen] = '\0';
	else
		strcpy (applName, "");
//	}	

	// construct loggerId and register it.
	snprintf(loggerId, MAXLEN-1, "%s@%s", basename(applName), hostName);
#ifdef HAVE_LOG4CPLUS
	log4cplus::getNDC().push(loggerId);
#endif // HAVE_LOG4CPLUS
}

#ifdef HAVE_LOG4CPLUS
using namespace log4cplus;

//# ------------------------ implement the five trace levels ------------------------
const LogLevel	TRACE1_LOG_LEVEL	= 1;
const LogLevel	TRACE2_LOG_LEVEL	= 2;
const LogLevel	TRACE3_LOG_LEVEL	= 3;
const LogLevel	TRACE4_LOG_LEVEL	= 4;
const LogLevel	TRACE5_LOG_LEVEL	= 5;
const LogLevel	TRACE6_LOG_LEVEL	= 6;
const LogLevel	TRACE7_LOG_LEVEL	= 7;
const LogLevel	TRACE8_LOG_LEVEL	= 8;

#define _TRACE1_STRING	LOG4CPLUS_TEXT("TRACE1")
#define _TRACE2_STRING	LOG4CPLUS_TEXT("TRACE2")
#define _TRACE3_STRING	LOG4CPLUS_TEXT("TRACE3")
#define _TRACE4_STRING	LOG4CPLUS_TEXT("TRACE4")
#define _TRACE5_STRING	LOG4CPLUS_TEXT("TRACE5")
#define _TRACE6_STRING	LOG4CPLUS_TEXT("TRACE6")
#define _TRACE7_STRING	LOG4CPLUS_TEXT("TRACE7")
#define _TRACE8_STRING	LOG4CPLUS_TEXT("TRACE8")

tstring traceLevel2String(LogLevel ll) {
	switch (ll) {
	case TRACE1_LOG_LEVEL:	return _TRACE1_STRING;
	case TRACE2_LOG_LEVEL:	return _TRACE2_STRING;
	case TRACE3_LOG_LEVEL:	return _TRACE3_STRING;
	case TRACE4_LOG_LEVEL:	return _TRACE4_STRING;
	case TRACE5_LOG_LEVEL:	return _TRACE5_STRING;
	case TRACE6_LOG_LEVEL:	return _TRACE6_STRING;
	case TRACE7_LOG_LEVEL:	return _TRACE7_STRING;
	case TRACE8_LOG_LEVEL:	return _TRACE8_STRING;
	}

	return tstring();		// not found
}

LogLevel string2TraceLevel (const tstring& lname) {
	if (lname == _TRACE1_STRING)	return TRACE1_LOG_LEVEL;
	if (lname == _TRACE2_STRING)	return TRACE2_LOG_LEVEL;
	if (lname == _TRACE3_STRING)	return TRACE3_LOG_LEVEL;
	if (lname == _TRACE4_STRING)	return TRACE4_LOG_LEVEL;
	if (lname == _TRACE5_STRING)	return TRACE5_LOG_LEVEL;
	if (lname == _TRACE6_STRING)	return TRACE6_LOG_LEVEL;
	if (lname == _TRACE7_STRING)	return TRACE7_LOG_LEVEL;
	if (lname == _TRACE8_STRING)	return TRACE8_LOG_LEVEL;

	return NOT_SET_LOG_LEVEL;			// not found
}

LOFAR::LoggerReference	theirTraceLoggerRef("TRC");		// create the tracelogger

#endif // HAVE_LOG4CPLUS

// initTracemodule
//
// Function that is used when the TRACE levels are NOT compiled out. It registers
// the TRACEn management routines at the Log4Cplus LogLevelManager and sets up the
// global trace-logger named "TRACE", with the additivity set to false.
// Attached to the trace-logger is one Appender that logs to stderr.
//
void initTraceModule (void) {
#ifdef HAVE_LOG4CPLUS
	//# register our own loglevels
	getLogLevelManager().pushToStringMethod(traceLevel2String);
	getLogLevelManager().pushFromStringMethod(string2TraceLevel);
	
	//# Setup a property object to initialise the TRACE Logger
	helpers::Properties		traceProp;		
	traceProp.setProperty("log4cplus.logger.TRC", "TRACE1, STDERR");
	traceProp.setProperty("log4cplus.additivity.TRC", "false");
	traceProp.setProperty("log4cplus.appender.STDERR", "log4cplus::ConsoleAppender");
	traceProp.setProperty("log4cplus.appender.STDERR.logToStdErr", "true");
	traceProp.setProperty("log4cplus.appender.STDERR.layout","log4cplus::PatternLayout");
	traceProp.setProperty("log4cplus.appender.STDERR.layout.ConversionPattern",
							"%D{%y%m%d %H%M%S,%q} [%t] %-6p %c{3} - %m%n");

	PropertyConfigurator(traceProp).configure();
	Logger::getInstance("TRC").forcedLog(0, "TRACE module activated");

#endif // HAVE_LOG4CPLUS
}

}	// namespace LOFAR
