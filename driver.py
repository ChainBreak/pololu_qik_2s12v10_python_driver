#!/usr/bin/env python

import serial

ser = serial.Serial('/dev/serial0',9600,timeout=1)


#ser.write('hello')
#print(ser.read(5))

id = 10
buf = bytearray([170,id,13,0])
#help(ser)
ser.write(buf)

##while True:
##    ser.flushInput()
##    ser.flushOutput()
##    buf = bytearray([0xaa,id,0x02])
##    for n in buf:
##        print(int(n))
##    ser.write(buf)
##    a = bytearray(ser.read(1))
##    for n in a:
##        print(int(n))
