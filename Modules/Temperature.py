#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Apr 22, 2017

@author: Eugene Melnikov
'''

import RPi.GPIO as GPIO
from tools import DHT11
from threading import Thread
from threading import enumerate as trenumerate
from tools import Confreader
from os import mknod
from os import path
from os import remove
from time import sleep

class RunClass(Thread):
    
    def __init__(self, operations=None):
        self.temp = 0
        self.hum = 0
        self.config = Confreader.ReadConfig()
        self.homedir = self.config.get_homedir()
        self.operations = operations
        Thread.__init__(self)
        self.daemon = False
        return
    
    #Obligatory functions
    
    def run(self):
        while True:
            if self.status():
                result = self.instance.read()
                if result.is_valid():
                    self.temp = result.temperature
                    self.hum = result.humidity
                sleep(1)
            else:
                return
        return
    
    def up(self):
        if not self.status():
            mknod(self.homedir + 'temperature.lock')
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.cleanup()
            self.instance = DHT11.DHT11(pin=4)
            GPIO.setmode(GPIO.BCM)
            self.start()
            #print trenumerate()
        return
    
    def stop(self):
        '''
        if self.status():
            try:
                remove(self.homedir + 'temperature.lock')
                self.hum = 0
                self.temp = 0
            except Exception as e:
                self.operations.logger.error(str(e))
                return False
            else:
                return True
        else:
            return False
        '''
        return
    
    def status(self):
        if path.isfile(self.homedir + 'temperature.lock'):
            return True
        else:
            return False
        return
    
    def info(self):
        return 'Temperature device'