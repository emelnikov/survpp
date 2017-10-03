#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Dec 28, 2016

@author: Eugene Melnikov
'''

from tools import Confreader
from importlib import import_module
import logging

class Operations(object):
    '''
    Class provides base actions to operate the system.
    '''
    
    def __init__(self, interface_modules=None, config_path=None):
        #for tests
        if config_path is None:
            self.config = Confreader.ReadConfig()
        else:
            self.config = Confreader.ReadConfig(config_path)

        self.install_mode = False
        logging.basicConfig(filename=self.config.get_homedir() + self.config.get_log_file(), format=self.config.get_log_format())
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.config.get_log_level())
        if type(interface_modules) != None:
            self.interface_modules = interface_modules
        self.device_modules = dict()
        self.device_instances = dict()
        return
    
    def install_all(self):
        self.install_mode = True
        interfaces = self.config.get_interfaces()
        devices = self.config.get_devices()
        interface_modules = dict()
        interface_instances = dict()
        device_modules = dict()
        device_instances = dict()
        print '\033[92m' + u'Installing interfaces...' + '\033[0m'
        for interface in interfaces:
            interface_modules[interface[1]] = import_module('Interfaces.' + interface[1])
            try:
                interface_instances[interface[1]] = interface_modules[interface[1]].InstallClass()
                print '\033[94m' + u'Installing ' + interface[1] + u' inteface' + '\033[0m'
                interface_instances[interface[1]].install()
            except AttributeError:
                print '\033[93m' + u'Interface ' + interface[1] + u' does not require installation' + '\033[0m'
            except Exception as e:
                print str(e)
                print '\033[91m' + u'Interface ' + interface[1] + u' cannot be installed' + '\033[0m'
                continue
        print '\033[92m' + u'Installing devices...' + '\033[0m'
        for device in devices:
            device_modules[device[1]] = import_module('Modules.' + device[1])
            try:
                device_instances[device[1]] = device_modules[device[1]].InstallClass()
                print '\033[94m' + u'Installing ' + device[1] + u' device' + '\033[0m'
                device_instances[device[1]].install()
            except AttributeError:
                print '\033[93m' + u'Device ' + device[1] + u' does not require installation' + '\033[0m'
            except Exception as e:
                print str(e)
                print '\033[91m' + u'Device ' + interface[1] + u' cannot be installed' + '\033[0m'
                continue
        return
    
    #Devices
    
    def run_devices(self, restore=False):
        '''
        Runs available devices.
        Checks core.conf for available devices in 'Devices' section, loads them, creates their instances and uses 'run_device()' function to start them one-by-one.
        If device also specified in 'Obligatory Devices' section of the config, it will be started anyway, despite of the face whether it was running before system was interrupted and started again.
        
        Accepts: restore - used to say 'run_device' function that this is initial system launch and states of devices should be restored. False by default.
        Returns: True - if there were no exceptions during devices launch, False - if there was an exception.
        '''
        
        devices = self.config.get_devices()
        try:
            for device in devices:
                if device[1] not in self.device_modules:
                    self.device_modules[device[1]] = import_module("Modules." + device[1])
                    self.device_instances[device[1]] = self.device_modules[device[1]].RunClass(self)
                #if devices are being launched on system start-up
                if restore:
                    #obligatory devices should be started in any case
                    if self.is_obligatory(device[1], 'device'):
                        self.device_instances[device[1]].up() #starting regardlress of status
                    else:
                        self.run_device(device[1], restore) #start if status is TRUE
                    print device[1]
                #if device is being launched manually from interface or by other device
                elif not restore:
                    self.run_device(device[1]) #start if status is FALSE
        except Exception as e:
            self.logger.error(str(e))
            return False
        else:
            return True
        return
    
    def run_device(self, device_name, restore=False):
        '''
        Launches device by its name.
        The function checks device status, and if the device is not running or it is not 'restore' procedure (see 'run_devices' function), 'up()' function of device is called to started it.
        
        Accepts: device name - name of the device which should be started, restrte - flag showing that the system was just started and device should be launched regardless of its status.
        Returns: True - if devices was started, False - if devices was not started (it is already running and it is not initial system launch)
        '''
        if restore:
            if self.device_instances[device_name].status():
                self.device_instances[device_name].up()
                return True
            else:
                return False
        elif not restore:
            if not self.device_instances[device_name].status():
                #print "starting device " + device_name
                self.device_instances[device_name].up()
                return True;
            else:
                return False
    
    def stop_devices(self):
        '''
        Stops all devices.
        The function calls 'stop()' function of each device instance in the 'device_instances' dict.
        
        Accepts: nothing
        Returns: True - if all devices were successfully stopped, False - if some exception arised during the procedure.
        '''
        
        try:
            for device in self.device_instances:
                self.device_instances[device].stop()
        except Exception as e:
            self.logger.error(str(e))
            return False
        else:
            return True
    
    def stop_device(self, device_name):
        '''
        Stops device by its name.
        
        Accepts: device_name - name of the devices which should be stopped.
        Returns: True - if device was stopped without exceptions, False - if there were some exceptions during the procedure.
        '''
        
        try:
            self.device_instances[device_name].stop()
        except Exception as e:
            self.logger.error(str(e))
            return False
        else:
            return True

    def get_device_config(self, device):
        try:
            methods = self.config.get_config('config/modules/' + device + '.conf')
        except Exception as e:
            self.logger.warning('There is no config for ' + device + ' device')
        else:
            return False
        return
    
    #Interfaces
    
    def run_interfaces(self, restore=False):
        interfaces = self.config.get_interfaces()
        self.interface_modules = dict()
        self.interface_instances = dict()
        try:
            for interface in interfaces:
                self.interface_modules[interface[1]] = import_module("Interfaces." + interface[1])
                self.interface_instances[interface[1]] = self.interface_modules[interface[1]].RunClass(self)
                #Run all interfaces with locks on first launch
                if self.is_obligatory(interface[1], 'interface'):
                    print interface[1]
                    self.run_interface(interface[1], restore)
                elif restore:
                    print interface[1]
                    self.run_interface(interface[1], restore)
        except TypeError as e:
            print str(e)
        else:
            return True
        return
    
    def stop_interfaces(self):
        return
    
    def run_interface(self, interface_name, restore=False):
        #Usual single iterface run
        if not self.interface_instances[interface_name].status() and not restore:
            self.interface_instances[interface_name].up()
            return True
        #Run interface on system start, regardless of status
        elif restore:
            self.interface_instances[interface_name].up()
            return True
        else:
            return False
    
    def stop_interface(self, interface_name):
        obligatory = self.config.get_obligatory_interfaces()
        is_obligatory = False
        for item in obligatory:
            if interface_name in item:
                is_obligatory = True
        if is_obligatory:
            self.logger.warning('Interface "' + interface_name + '" is obligatory and cannot be stopped')
        else:
            self.interface_instances[interface_name].stop()
        return

    #Misc
    
    def get_statuses(self):
        '''
        Provides status of the system. Particularly statuses (UP/DOWN) of each interface and device.
        
        Accepts: nothing
        Returns: status as string
        '''
        
        result = {'interfaces': dict(), 'devices': dict()}
        for instance in self.interface_instances:
            if self.interface_instances[instance].status():
                status = 'UP'
            else:
                status = 'DOWN'
            result['interfaces'][self.interface_instances[instance].info()] = status
        for device in self.device_instances:
            if self.device_instances[device].status():
                status = 'UP'
            else:
                status = 'DOWN'
            result['devices'][self.device_instances[device].info()] = status
        return result

    def list_devices(self):
        result = list()
        for device in self.device_instances:
            result.append(device)
        return result

    def list_interfaces(self):
        result = list()
        for interface in self.interface_instances:
            result.append(interface)
        return result
    
    def is_obligatory(self, module, mod_type):
        '''
        Checks if module name specified in 'Obligtary' section of core.conf.
        
        Accepts: module name (string), module type (device/interface, string)
        Returns: True - if module is found in 'Obligatory' section, False - if not
        '''
        
        if mod_type == 'interface':
            obligatory = self.config.get_obligatory_interfaces()
        elif mod_type == 'device':
            obligatory = self.config.get_obligatory_devices()
        for obl in obligatory:
            if module in obl:
                return True
        else:
            return False