#!/usr/bin/env python

import serial
import time

ser = serial.Serial('/dev/serial0',9600,timeout=1)


#ser.write('hello')
#print(ser.read(5))

id = 10
buf = bytearray([170,id,0x08,127])
#help(ser)
ser.write(buf)
try:
    while True:
        ser.flushInput()
        buf = bytearray([0xaa,id,0x10])
        ser.write(buf)
        a = bytearray(ser.read(1))
        print("%i mA" % (int(a[0])*150))
except KeyboardInterrupt:
    pass



buf = bytearray([170,id,0x08,0])
#help(ser)
ser.write(buf)
