//#  testSockt.cc: Manual program to test Net/Socket code
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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

#include <lofar_config.h>
#include <TimBase/lofar_string.h>
#include <TimBase/Net/Socket.h>
#include <TimBase/LofarLogger.h>

#include <fcntl.h>

using namespace LOFAR;

static	Socket*		dataSock = 0;
static	Socket*		testSock;


//
// doConnect
//
void doConnect()
{
	if (testSock->isConnected()) {
		cout << "Already connected" << endl;
		return;
	}

	int32	waitMs;
	cout << "Wait how many millisecs: ";
	cin >> waitMs;

	if (testSock->isServer()) {
		dataSock = testSock->accept(waitMs);
		if (dataSock != 0) {		// successful ??
			return;
		}
		cout << "accept returned error:" << testSock->errstr() << endl;
		return;
	}

	// client code
	int32	result = testSock->connect(waitMs);
	switch (result) {
	case Socket::SK_OK:
		dataSock = testSock;
		break;
	case Socket::INPROGRESS:
		cout << "timeout on connect" << endl;
		break;
	default:
		cout << "connect returned error:" << testSock->errstr() << endl;
	}
}

void doRead(bool	blocking)
{
	int32	nrBytes;
	int32	bytesRead;
	char	buf [1025];

	cout << "Wait for how many bytes [max 1024]: ";
	cin	>> nrBytes;

	if (nrBytes < 0)		nrBytes = 1;
	if (nrBytes > 1024)		nrBytes = 1024;

	if (blocking)
		bytesRead = dataSock->readBlocking(buf, nrBytes);
	else
		bytesRead = dataSock->read(buf, nrBytes);
	cout << "read returned value " << bytesRead << endl;

	if (bytesRead < 0) {
		cout << "error: " << dataSock->errstr();
		return;
	}

	buf[bytesRead] = '\0';
	cout << "received:[" << buf << "]" << endl;

}

void doWrite(bool	blocking)
{
	int32	bytesWrtn;
	string	buf;

	cout << "Type message to send to other side: ";
	cin	>> buf;

	if (blocking)
		bytesWrtn = dataSock->writeBlocking(buf.c_str(), buf.length());
	else
		bytesWrtn = dataSock->write(buf.c_str(), buf.length());
	cout << "write returned value " << bytesWrtn << endl;

	if (bytesWrtn < 0) {
		cout << "error: " << dataSock->errstr();
		return;
	}
}

void showMenu()
{
	cout << endl << endl << endl;
	if (testSock->isServer()) 
		cout << "Serversocket is ";
	else
		cout << "Clientsocket is ";
	if ((dataSock && dataSock->isConnected()) || testSock->isConnected()) {
		cout << "connected (";
		if (!testSock->isBlocking())
			cout << "NON";
		cout << "blocking) at port " << testSock->port() << endl;
	}
	else {
		cout << "not yet connected" << endl;
	}

	cout << "Commands:" << endl;
	cout << "c		Connect to other side" << endl;
	cout << "n		set nonblockingmode" << endl;
	cout << "b		set blockingmode" << endl << endl;;

	if (dataSock && dataSock->isConnected())  {
		cout << "w		write some data" << endl;
		cout << "r		read some data" << endl;
		cout << "W		write some data BLOCKING" << endl;
		cout << "R		read some data BLOCKING" << endl;
	}

	cout << endl << "q		quit" << endl;
	cout << endl << "Enter letter of your choice: ";
}


char getMenuChoice()
{
	char	choice;

	for (;;) {
		showMenu();
		cin >> choice;
		switch (choice) {
			case 'c':
			case 'n':
			case 'b':
			case 'q':
				return (choice);

			case 'r':
			case 'w':
			case 'R':
			case 'W':
				if (dataSock && dataSock->isConnected())
					return (choice);
				break;
		}
		cout << "Sorry wrong choice" << endl;
	}
}

int main (int32	argc, char*argv[]) {
	
	
	switch (argc) {
	case 2:
		testSock = new Socket("testServer", argv[1], Socket::TCP);
		break;
	case 3:
		testSock = new Socket("testClient", argv[1], argv[2], Socket::TCP);
		break;
	default:
		cout <<"Syntax: " << argv[0] << " service port   - be a client" << endl;
		cout <<"        " << argv[0] << " port           - be a server" << endl;
		return (-1);
	}

	char		theChoice = ' ';
	while (theChoice != 'q') {
		switch (theChoice = getMenuChoice()) {
		case 'c':
			doConnect();
			break;
		case 'n':
			testSock->setBlocking(false);
			if (dataSock)
				dataSock->setBlocking(false);
			break;
		case 'b':
			testSock->setBlocking(true);
			if (dataSock)
				dataSock->setBlocking(true);
			break;
		case 'r':
			doRead(false);
			break;
		case 'w':
			doWrite(false);
			break;
		case 'R':
			doRead(true);
			break;
		case 'W':
			doWrite(true);
			break;
		case 'x':
			break;
		}
	}

	if (dataSock)
		delete dataSock;
	delete testSock;

	return (0);
}

