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

class RunClass():
    
    def __init__(self, operations=None):
        self.operations = operations
    
    def up(self):
        self.threadinstance = ThreadClass(self, self.operations)
        if not self.status():
            mknod(self.threadinstance.homedir + 'alarm.lock')
            self.threadinstance.start()
        return
    
    def stop(self):
        if self.status():
            try:
                remove(self.threadinstance.homedir + 'alarm.lock')
            except Exception as e:
                self.operations.logger.error(str(e))
                return False
            return True
        else:
            return False
    
    def status(self):
        if path.isfile(self.threadinstance.homedir + 'alarm.lock'):
            return True
        else:
            return False
    
    def info(self):
        return 'Alarm device'
    
    #Custom functions
    
    def play_alarm(self):
        if self.status():
            self.threadinstance.playing = True
            return True
        else:
            return False
    
    def stop_alarm(self):
        self.threadinstance.playing = False
        return

class ThreadClass(Thread):
    
    def __init__(self, runinstance, operations=None):
        self.config = Confreader.ReadConfig()
        self.homedir = self.config.get_homedir()
        self.playing = False
        Thread.__init__(self)
        self.daemon = False
        self.operations = operations
        self.runinstance = runinstance
        return
    
    #Obligatory functions
    
    def run(self):
        #waiting loop
        while self.runinstance.status():
            if self.playing and self.runinstance.status():
                alarm_list = ['sounds/alarm1.wav', 'sounds/alarm2.wav']
                self.playing = True
                while self.playing:
                    for alarm in alarm_list:
                        try:
                            call(['play', self.homedir + alarm])
                        except Exception as e:
                            self.operations.logger.error(str(e))
            else:
                sleep(0.5)
        return