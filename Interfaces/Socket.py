#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Dec 27, 2016

@author: Eugene Melnikov
'''

from threading import Thread
from time import sleep
from json import loads
from tools import Confreader
from os import mknod
from os import path
from os import remove
import socket
from __builtin__ import True

class RunClass(Thread):

    def __init__(self, operations=None):
        if type(operations) != None:
            self.interface_modules = operations.interface_modules
        self.operations = operations
        Thread.__init__(self)
        self.daemon = True
        self.config = Confreader.ReadConfig()
        
    def run(self):
        self.trigger = True
        self.sock = self.open_socket()
                    
        while self.trigger:
            conn, addr = self.sock.accept()
            self.operations.logger.info('Connected:' + str(addr))
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    else:
                        try:
                            data_decoded = loads(data)
                        except Exception as e:
                            self.operations.logger.error(str(e))
                        else:
                            #logic here
                            for method, params in data_decoded.items():
                                if method == 'stop_interface':
                                    self.operations.stop_interface(params)
                                elif method == 'start_interface':
                                    self.operations.run_interface(params)
                                elif method == 'alarm_interface':
                                    self.alarm_interface(params)
                                else:
                                    self.operations.logger.warning('Unknown method was used: ' + method + ' with parameters: ' + params)
                            conn.send(data.upper())
            except Exception as e:
                self.operations.logger.error(str(e))
                conn.close()
            else:
                self.operations.logger.info('Connection was closed by the server')
                conn.close()
                sleep(1)
                
    def up(self):
        if not path.isfile('config/socket.conf'):
            self.operations.logger.error('Socket interface is not installed')
            return
        if not path.isfile(self.config.get_homedir() + 'socket.lock'):
            mknod(self.config.get_homedir() + 'socket.lock')
        self.start()
    
    def stop(self):
        self.trigger = False
        self.sock.close()
        remove(self.config.get_homedir() + 'socket.lock')
        return True
    
    def status(self): #provides status of interface (UP:True/DOWN:False)
        if path.isfile(self.config.get_homedir() + 'socket.lock'):
            return True
        else:
            return False
        
    def notify(self):
        return True
    
    def info(self):
        return "Socket interface"
    
    #Custom functions
    
    def open_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_address = self.config.get_custom_value('config/socket.conf', 'General', 'bind_address')
        bind_port = self.config.get_custom_value('config/socket.conf', 'General', 'bind_port')
        sock.bind((bind_address, int(bind_port)))
        sock.listen(1)
        return sock
    
    def alarm_interface(self, data):
        interface_name = data['interface_name']
        try:
            self.operations.interface_instances[interface_name].notify(data)
        except Exception as e:
            self.operations.logger.error(str(e))
            return False
        else:
            return True
        
class InstallClass(object):
    
    def __init__(self):
        return
    
    def install(self):
        '''
        Installs Socket interface.
        The function generates socket.conf file, based on bind address and port entered by user during installation.
        
        Accepts: nothing
        Returns: True - in case of successful installation, False - if there were any exceptions or interface is already installed
        '''
        
        if not path.isfile('config/socket.conf'):
            try:
                from ConfigParser import RawConfigParser
                config = RawConfigParser()
                config.add_section('General')
                bind_address = raw_input(u'Enter address allowed to connect, leave empty to allow all: ')
                config.set('General', 'bind_address', bind_address)
                bind_port = raw_input(u'Enter port: ')
                config.set('General', 'bind_port', bind_port)
                with open('config/socket.conf', 'wb') as configfile:
                    config.write(configfile)
            except Exception as e:
                print str(e)
                return False
            print u'Socket interface has been installed'
        else:
            print u'Socket interface is already installed'
            return False
        return True
