# IOTA Pymessenger
	A Chat messenger written purely on Python and make use of PyQt5, Qt5 () for UI Designing

## Requirements
	Ubuntu 16.04
	Python 3+
	Virtualenv

## Instructions
1. Make sure "iotaproxy_npm" (see below) is setup accordingly and ready to run.
2. All requirements meet
3. Create a virtual environment for python3
4. From inside virtualenv, enter "messengerapp" directory:
```
cd messengerapp
```
5. Install the requirements.txt:
```
pip install -r requirements.txt
```
6. Run the app with main.py:
```
python main.py
```

# iotaproxy
	A simple proxy server for the IOTA tangle network, supporting the attachToTangle command (PoW)
	source: https://github.com/TimSamshuijzen/iotaproxy

## Requirements
	Node.js

## Instructions
1. Enter the "iotaproxy_npm" directory:
```
cd iotaproxy_npm
```
2. Install the dependiences:
```
npm install
```
3. Edit index.js to set preferred connection to public iota node. For example:
```
iotaProxy.start(
  {
    host: 'http://node02.iotatoken.nl', // PUBLIC IOTA NODE, used to relay traffic to tangle.
    port: 14265,						// Port of PUBLIC NODE
    localPort: 14265,					// Listening on http://localhost for light node to send request to the proxy
    overrideAttachToTangle: true,		// Do the POW on proxy before replay to tangle because public node doesnot support for POW
    timeout: 15							// Time out in minutes
  }
);
```
4. Run the proxy server:
```
npm start
```

# Previews
1. User begins be loggings to the app using IOTA personal seed
![alt text](https://raw.githubusercontent.com/benuha/IOTA-PyMessenger/master/images/1_iota_chat_login_windows.png)

In Linux, the seed can be generated by executing:
```
$ cat /dev/urandom | tr -dc A-Z9 | head -c${1:-81}
```

2. The app then presents with simple chat windows:
![alt text](https://raw.githubusercontent.com/benuha/IOTA-PyMessenger/master/images/3_iota_chat_chat_windows_history_.png)

# License
All projects licensed under the GNU General Public License (GPL) version 3, with the exception of Qt Software.

For open-source licensed Qt, some specific parts (modules) are not available under the GNU LGPL version 3, but under the GNU General Public License (GPL) instead. See the list of Qt modules for details. For commercial licensees, all modules are available under a single, commercial Qt license.
