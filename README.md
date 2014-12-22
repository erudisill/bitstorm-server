BitStorm Server
===============

Small console server which reads BitStorm network data locally and streams via TCP Sockets.  
Implemented using a Python SocketServer with the ThreadingMixin for handling multiple clients.
Current version includes a serial port listener, but plans are to make that more generic
for serving up recorded test data, random values, stress data, etc.


Related Projects
----------------
Bitstorm Workbench will act as a client to the BitStorm Server.


Caveats
-------
	* Purely console driven, requires Ctl-C to exit
	* No logging at the moment
	* Pretty sparse exception handling - this is primarily a development tool ;)

Dependencies
------------
pyserial
jsonpickle