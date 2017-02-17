#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Dec 14, 2016

@author: Eugene Melnikov
'''

from ConfigParser import RawConfigParser
from __builtin__ import int

class ReadConfig(RawConfigParser):
    '''
    Class provides simplified functions to access config values and whole sections.
    May accepts core.conf file path as argument.
    '''
    
    def __init__(self, filename='config/core.conf'):
        self.config = RawConfigParser()
        self.filename = filename
    
    #Common
    
    def get_config(self, filename):
        '''
        Provides config reader object.
        
        Accepts: config file path (string)
        Returns: config reader object (RawConfigParser instance)
        '''
        
        readerObj = self.config
        readerObj.read(filename)
        return readerObj
    
    def get_homedir(self):
        '''
        Provides home directory path specified in core.conf.
        
        Accepts: nothing
        Returns: home directory path as string
        '''
        
        result = self.get_config(self.filename).get('General', 'homedir')
        return result
    
    def get_log_file(self):
        '''
        Provides log file name specified in core.conf.
        
        Accepts: nothing
        Returns: log file name as string
        '''
        
        result = self.get_config(self.filename).get('Logger', 'logfile')
        return result
    
    def get_log_format(self):
        '''
        Provides format of output to log file specified in core.conf.
        
        Accepts: nothing
        Returns: log output format as string
        '''
        
        result = self.get_config(self.filename).get('Logger', 'format')
        return result
    
    def get_log_level(self):
        '''
        Provides logging level specified in core.conf.
        
        Accepts: nothing
        Returns: logging level value as int
        '''
        
        result = int(self.get_config(self.filename).get('Logger', 'level'))
        return result
    
    #Devices
    
    def get_devices(self):
        '''
        Provides list of all devices specified in core.conf.
        
        Accepts: nothing
        Returns: list of tuples [('key', 'device_name')]
        '''
        
        result = self.get_config(self.filename).items('Devices')
        return result
    
    def get_obligatory_devices(self):
        '''
        Provides list of all obligatory devices specified in core.conf.
        
        Accepts: nothing
        Returns: list of tuples [('key', 'obligatory_device_name')]
        '''
        
        result = self.get_config(self.filename).items('Obligatory Devices')
        return result
    
    #Interfaces
    
    def get_interfaces(self):
        '''
        Provides list of all interfaces specified in core.conf.
        
        Accepts: nothing
        Returns: list of tuples [('key', 'interface_name')]
        '''
        
        result = self.get_config(self.filename).items('Interfaces')
        return result
    
    def get_obligatory_interfaces(self):
        '''
        Provides list of obligatory interfaces specified in core.conf.
        
        Accepts: nothing
        Returns list of tuples [('key', 'obligatory_interface_name')]
        '''
        
        result = self.get_config(self.filename).items('Obligatory Interfaces')
        return result
        
    #Misc
    
    def get_custom_value(self, filename, section, value):
        '''
        Provides value from specified config file and its section.
        
        Accepts: file path (string), section (string), value name (string)
        Returns: custom value as string
        '''
        
        result = self.get_config(filename).get(section, value)
        return result
    
    def get_custom_section(self, filename, section):
        '''
        Provides whole section from specified config file.
        
        Accepts: config file path (string), section name (string)
        Returns: list of tuples [('key', 'value')]
        '''
        
        result = self.get_config(filename).items(section)
        return result