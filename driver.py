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
        self.ser.flush()
        
        readBuf = self.ser.read(receiveLength)
        res = array.array("B",readBuf)
        return res
        
        


class MotorController:
    def __init__(self,driver,deviceID):
        self.driver = driver
        self.id = deviceID
        self.params = self.getAllConfigParams()
    
    def stopAll(self):
        self.setMotorSpeed(0,0)
        self.setMotorSpeed(1,0)

    def getFirmwareVersion(self):
        res = self.driver.sendReceive([0xaa,self.id,0x01],1)
        v = res[0] - 48
        return v

    def getConfigParam(self,paramNumber):
        res = self.driver.sendReceive([0xaa,self.id,0x03,paramNumber],1)
        return res[0]

    def setConfigParam(self,paramNumber, value):
        currentValue = self.getConfigParam(paramNumber)
        if currentValue != value:
            error = self.driver.sendReceive([0xaa,self.id,0x04,paramNumber,value,0x55,0x2a],1)
            if not error[0]:
                self.params[paramNumber] = value
            return error[0]
        
    def getAllConfigParams(self):
        params = [0]*12
        for i in range(12):
            params[i] = self.getConfigParam(i)
        return params

    def getErrors(self):
        res = self.driver.sendReceive([0xaa,self.id,0x02],1)
        return res[0]
    
    def setMotorSpeed(self,motorID,speed):
        """motorID 0 or 1, speed -1.0 to 1.0"""
        speed = max(min(speed,1.0),-1.0) #range limit
        direction = speed < 0 # set reverse direction bit if speed less than 0
        bit8speed = self.params[1] & 1 #first bit of paramter 1 can be used to determin if its in 8 bit speed mode
        speedMultiplyer = 127 # speed is between 0-127 for 7bit speed mode
        if bit8speed:
            speedMultiplyer = 255 #speed is between 0-255 for 8bit speed mode
        speedByte = int(abs(speed)*speedMultiplyer)# covert floating speed to scaled byte
        
        cmd = speedByte >= 128 # bit 0 of command is used for 8th bit of speedbyte as speedbyte can only use 7 bits
        
        speedByte &= 127 #clear the 8th bit of the speedbyte as it can only use 7 bits
        
        cmd |= direction << 1 #shift direction into bit 1
        cmd |= motorID << 2 #shift motor id into bit 2
        cmd |= 1 << 3 # just set bit 3

        #send the speed command
        self.driver.sendReceive([0xaa,self.id,cmd,speedByte],0)
        
if __name__ == "__main__":
    import math
    d = SerialDriver('/dev/serial0',9600)

    c1 = d.getController(10)

    c1.getErrors()
    c1.getFirmwareVersion()
    c1.setConfigParam(3,4)

    for pwmMode in [0]:
        
        c1.setConfigParam(1,pwmMode)

        for n in range(0,12):
            val = c1.params[n]
            print("%2i: %i" % (n, val))

        deg = 0
        while deg < 6.3:
            deg += 0.05
            c1.setMotorSpeed(0,math.sin(deg))
            c1.setMotorSpeed(1,math.sin(deg))

    d.close()

    
