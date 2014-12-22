import logging
import serial
import threading
from binascii import hexlify

class CpSerialBytes(bytearray):
    def __str__(self, *args, **kwargs):
        hexline = hexlify(self)
        n = 2
        pairs = [hexline[i:i+n] for i in range(0, len(hexline), n)]
        final = ("[{0:03}] ".format(len(self)) + " ".join(pairs)).upper()
        return final
    
class CpSerialSettings():
    def __init__(self):
        self.timeout = 0
        self.port = ""
        self.baudrate = 38400
        self.parity = 'N'
        self.stopbits = 1
        self.bytesize = 8
        self.xonxoff = 0
        self.rtscts = 0
    
    def __str__(self):
        s =  self.port + " " + str(self.baudrate) + " " + str(self.bytesize) + \
             self.parity + str(self.stopbits)
        if self.xonxoff != 0:
            s = s + ",xonxoff"
        elif self.rtscts != 0:
            s = s + ",rtscts"
        return s

class CpSerialService(threading.Thread):
    
    def __init__(self, settings=None, loggerName='CpSerialService'):
        threading.Thread.__init__(self)
        self._putData = None
        self.stop_event = threading.Event()
        self.received_bytes = 0
        self.logger = logging.getLogger(loggerName)
        self.ser = serial.Serial()
        self.ser.timeout = 0
        self.ser.port = ""
        if not settings:
            self.ser.port = ""
            self.ser.baudrate = 38400
            self.ser.parity = 'N'
            self.ser.stopbits = 1
            self.ser.bytesize = 8
            self.ser.xonxoff = 0
            self.ser.rtscts = 0
        else:
            self.ser.port = settings.port
            self.ser.baudrate = settings.baudrate
            self.ser.parity = settings.parity
            self.ser.stopbits = settings.stopbits
            self.ser.bytesize = settings.bytesize
            self.ser.xonxoff = settings.xonxoff
            self.ser.rtscts = settings.rtscts
    
    def run(self):
        
        self.logger.info('starting CpSerialService...')
        
        data = bytearray()
        
        self.ser.open()
        self.logger.info('opened port ' + self.ser.port)
        
        while self.stop_event.is_set() == False:
            
            # handle incoming data
            del data[:]
            if (self.ser.inWaiting() > 0):
                data.extend(self.ser.read(self.ser.inWaiting()))
    
            if len(data) > 0:
                # log and signal data received
                self.received_bytes = self.received_bytes + len(data)
                if self._putData:
                    # send new copy of data
                    self._putData(CpSerialBytes(data))
            
            #time.sleep(0.005)
                    
        # shutdown the serial port
        self.ser.close() 
        
        self.logger.info('CpSerialService stopped!')

    def stop(self):
        if self.is_alive() == True:
            self.stop_event.set()
            self.join()
            
    def connectData(self, q):
        self._putData = q