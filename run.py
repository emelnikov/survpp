#!/usr/bin/python
# -*- coding: utf-8 -*-

from tools import Confreader
from tools import Operations
from time import sleep
from sys import argv

from ConfigParser import RawConfigParser
from os import path
from pkgutil import iter_modules
import unittest

class CoreRun(object):
    '''
    Class launches SURVPP system
    '''
    
    def __init__(self):
        self.config = Confreader.ReadConfig()
        self.operations = Operations.Operations()
        self.args = argv
    def run(self):
        '''
        Launches the system.
        Uses tools.Operations module to run devices and interfaces.
        Returns None.
        '''
                
        self.operations.logger.info('Core is starting...')
        self.operations.run_devices(True)
        self.operations.run_interfaces(True)
        self.operations.logger.info('Core has been started')
        while True:
            sleep(10)
        return
        
class CoreInstall(object):
    '''
    Class for Core survpp installation.
    '''
    
    def __init__(self):
        self.config = RawConfigParser(allow_no_value=True)
        self.config_path = 'config/core.conf'
        return
    
    def install(self):
        '''
        Installs the system.
        Function performs all required actions to make the system work. In particular it creates core.conf in runs install() function of each device and interface (if there is such function)
        
        Accepts: nothing
        Returns: True - if installation was successful, False - if some exceptions arised during the process.
        '''
        
        import Modules as devices_pkg
        import Interfaces as interfaces_pkg
        
        modules = list()
        interfaces = list()
        
        print '\033[92m' + u'Staring SURVPP installation...' + '\033[0m'
        try:
            for importer, modname, ispkg in iter_modules(devices_pkg.__path__):
                modules.append(modname)
            for importer, modname, ispkg in iter_modules(interfaces_pkg.__path__):
                interfaces.append(modname)
                    
            if not path.isfile(self.config_path):
                self.config.add_section('General')
                self.config.set('General', 'homedir', path.expanduser('~') + '/')
                
                self.config.add_section('Devices')
                for key, m in enumerate(modules):
                    self.config.set('Devices', 'dev' + str(key), m)
                    if key == 0:
                        devices_string = m
                    else:
                        devices_string += ', ' + m
                        
                self.config.add_section('Obligatory Devices')
                obl_devices_string = raw_input('Please specify obligatory devices using comma (case sensitive). Available devices: ' + devices_string + ': ')
                obl_devices_list = obl_devices_string.split(',')
                for key, obl_dev in enumerate(obl_devices_list):
                    self.config.set('Obligatory Devices', 'dev' + str(key), obl_dev.strip(' '))
                    
                self.config.add_section('Interfaces')
                for key, i in enumerate(interfaces):
                    self.config.set('Interfaces', 'int' + str(key), i)
                    if key == 0:
                        interfaces_string = i
                    else:
                        interfaces_string += ', ' + i
                        
                self.config.add_section('Obligatory Interfaces')
                obl_interfaces_string = raw_input('Please specify obligatory interfaces using comma (case sensitive). Available interfaces: ' + interfaces_string + ': ')
                obl_interfaces_list = obl_interfaces_string.split(',')
                for key, obl_int in enumerate(obl_interfaces_list):
                    self.config.set('Obligatory Interfaces', 'int' + str(key), obl_int.strip(' '))
                    
                self.config.add_section('Logger')
                self.config.set('Logger', 'logfile', 'survpp.log')
                self.config.set('Logger', ';levels: 0 - NOTSET, 10 - DEBUG, 20 - INFO, 30 - WARNING, 40 - ERROR, 50 - CRITICAL')
                self.config.set('Logger', 'level', '20')
                self.config.set('Logger', 'format', '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s')
                with open(self.config_path, 'wb') as configfile:
                    self.config.write(configfile)
                operations = Operations.Operations()
                operations.install_all()
                print '\033[92m' + u'Installation complete' + '\033[0m'
            else:
                print '\033[93m' + u'Core is already installed' + '\033[0m'
        except Exception as e:
            print str(e)
            return False
        else:
            return True

#STARTER

if len(argv) == 1:
    corerun = CoreRun()
    corerun.run()    
elif argv[1] == 'install':
    core_install = CoreInstall()
    core_install.install()
else:
    print u'Unknown agrument'