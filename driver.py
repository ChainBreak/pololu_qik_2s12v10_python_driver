#!/usr/bin/env python

#https://www.pololu.com/docs/0J29/all

import serial
import time
import array

class SerialDriver:
    """Serial Driver manages the serial connection, writing and read bytes and creating check sums"""

    def __init__(self,serialDevice,baud):
        self.ser = serial.Serial(serialDevice,baud,timeout=1)
        #help(self.ser)
        self.controllers = {}

    def close(self):
        for ctrl in self.controllers.itervalues():
            ctrl.stopAll()


    def getController(self,deviceID):
        """There could be multiple motor controlers on the serial connection so use the deviceID to create MotorController for the device you want to use"""
        if deviceID in self.controllers:
            return self.controllers[deviceID]
        else:
            newCtrl = MotorController(self,deviceID)
            self.controllers[deviceID] = newCtrl
            return newCtrl
        
    def sendReceive(self,sendArray, receiveLength):
        writeBuf = array.array("B",sendArray)
        #self.ser.flushOutput()
        self.ser.flushInput()
        
        self.ser.write(writeBuf)
        #self.ser.flush()
        
        readBuf = self.ser.read(receiveLength)
        res = array.array("B",readBuf)
        return res
        
        


class MotorController:
    def __init__(self,driver,deviceID):
        self.driver = driver
        self.id = deviceID
    
    def stopAll(self):
        self.setMotorSpeed(0,0)
        self.setMotorSpeed(1,0)

    def getFirmwareVersion(self):
        res = self.driver.sendReceive([0xaa,self.id,0x01],1)
        v = res[0] - 48
        return v

    def setMotorSpeed(self,motorID,speed):
        """motorID 0 or 1
        speed -1.0 to 1.0"""

        dir = speed >= 0

        byteSpeed = int(abs(speed)*127)
        
        cmd = 0
        cmd |= dir << 1
        cmd |= motorID << 2
        cmd |= 1 << 3

        self.driver.sendReceive([0xaa,self.id,cmd,byteSpeed],0)
        

import math
d = SerialDriver('/dev/serial0',9600)

c1 = d.getController(10)


c1.getFirmwareVersion()



deg = 0
while deg < 6:
    deg += 0.01
    c1.setMotorSpeed(0,math.sin(deg))
    c1.setMotorSpeed(1,math.sin(deg))

d.close()

    
