#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# Class
class RX(object):
  
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.threadStop  = False
        self.threadMutex = True
        self.READLEN     = 1024

    def thread(self): 
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN)
                if (nRx > 0):
                    self.buffer += rxTemp  
                time.sleep(0.01)

    def threadStart(self):       
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def getIsEmpty(self):
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    def getBufferLen(self):
        return(len(self.buffer))

    def getAllBuffer(self, len):
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    def getBuffer(self, nData):
        self.threadPause()
        b           = self.buffer[0:nData]
        self.buffer = self.buffer[nData:]
        self.threadResume()
        return(b)

    def getNData(self, size,timeout, use_timeout, time_count):
        timeout_value = 0
        if(use_timeout==0):
            while((self.getBufferLen() < size)and(timeout_value<=timeout)):
                time.sleep(0.05)                 
                timeout_value+= 0.05
        elif (use_timeout==2):
            while((self.getBufferLen() < size)and(timeout_value<=timeout)):
                time.sleep(0.05)                 
                timeout_value+= 0.05
            if (timeout_value>=timeout):
                time_count+=1
            return (self.getBuffer(size),time_count)
        else:    
            while(self.getBufferLen() < size):
                time.sleep(0.05)                 
                timeout_value+= 0.05
        return (self.getBuffer(size),time_count)

    def clearBuffer(self):
        self.buffer = b""


