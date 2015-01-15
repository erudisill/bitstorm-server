'''
Created on Dec 19, 2014

@author: ericrudisill
'''
import getopt
import sys
from settings import Settings
import jsonpickle
from cpSerial import CpSerialService
import time
from tcpserver import ThreadedTCPServer, ThreadedTCPRequestHandler
import threading

HOST, PORT = "localhost", 1337

def loadSettings(settingsFile=None):
    if not settingsFile:
        settingsFile = "settings.json"
    s = Settings()
    try:
        with open(settingsFile, "r") as f:
            j = f.read()
            s = jsonpickle.decode(j)
    except Exception, ex:
        print ex
        print "Settings file not found. Creating default template file. Add port there."
        with open(settingsFile, "w") as f:
            jsonpickle.set_encoder_options('json', indent=4)
            f.write(jsonpickle.encode(s))
        exit(2)

    s.filename = settingsFile
    
    return s


def main(argv):
    settingsFile = None
    try:
        opts, args = getopt.getopt(argv, "hs:", ["help","settings="])
    except getopt.GetoptError:
        print 'usage: bitstorm-server -s <settingsfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'usage: bitstorm-server -s <settingsfile>'
            sys.exit()
        elif opt in ("-s", "--settings"):
            settingsFile = arg
    
    settings = loadSettings(settingsFile)
    print "Loaded settings from " + settings.filename
    print str(settings)

    print "Starting TCP service."
    server = ThreadedTCPServer((HOST,PORT), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print "Starting serial service."
    serial = CpSerialService(settings.cpSerial)
    serial.connectData(server.putData)
    serial.start()
    
    print "Use Control-C to exit."
    
    do_exit = False
    while do_exit == False:
        try:
            if serial.records == -1:
                msg = "\rBytes: {0}     Clients: {1}     ".format(serial.received_bytes, server.clientsCount())
            else:
                msg = "\rBytes: {0}     Records: {1}      Clients: {2}     ".format(serial.received_bytes, serial.records, server.clientsCount())
            sys.stdout.write(msg)
            sys.stdout.flush()
            time.sleep(0.1)
        except KeyboardInterrupt:
            do_exit = True
         
    server.shutdown()   
    serial.stop()
    
    print "\r\nDone"
    
if __name__ == '__main__':
    print "\r\nBitStorm Server"
    main(sys.argv[1:])