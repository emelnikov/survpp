#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Jan 3, 2017

@author: Eugene Melnikov
'''

from os import mknod
from os import path
from os import remove
from tools import Confreader
from threading import Thread
from subprocess import call
from time import sleep

class RunClass(Thread):
    
    def __init__(self, operations=None):
        self.config = Confreader.ReadConfig()
        self.homedir = self.config.get_homedir()
        self.playing = False
        Thread.__init__(self)
        self.daemon = True
        self.operations = operations
        return
    
    #Obligatory functions
    
    def run(self):
        #waiting loop
        while True:
            if self.playing and self.status():
                alarm_list = ['sounds/alarm1.wav', 'sounds/alarm2.wav']
                self.playing = True
                while self.playing:
                    for alarm in alarm_list:
                        print self.homedir + alarm
                        try:
                            call(['play', self.homedir + alarm])
                        except Exception as e:
                            self.operations.logger.error(str(e))
            else:
                sleep(0.5)
                
    
    def up(self):
        if not self.status():
            mknod(self.homedir + 'alarm.lock')
        self.start()
        return
    
    def stop(self):
        if self.status():
            try:
                remove(self.homedir + 'alarm.lock')
            except Exception as e:
                self.operations.logger.error(str(e))
                return False
            else:
                return True
        else:
            return False
    
    def status(self):
        if path.isfile(self.homedir + 'alarm.lock'):
            return True
        else:
            return False
    
    def info(self):
        return 'Alarm device'
    
    #Custom functions
    
    def play_alarm(self):
        if self.status():
            self.playing = True
        return True
    
    def stop_alarm(self):
        self.playing = False
        return