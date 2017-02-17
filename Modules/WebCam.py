#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 18 дек. 2016 г.

@author: Eugene Melnikov
'''

from subprocess import call
from os import path
from os import kill
from shutil import copy
import unittest

class RunClass(object):
    
    def __init__(self, operations=None):
        #importing Confreader here in order to allow unit tests to work
        from tools import Confreader
        
        self.config = Confreader.ReadConfig()
        self.homedir = self.config.get_homedir()
        self.operations = operations
    
    #Obligatory functions
    
    def up(self):
        motion_config = self.config.get_custom_value('config/webcam.conf', 'General', 'motion_config')
        try:
            call(['motion', '-c', self.homedir + motion_config])
        except Exception as e:
            self.operations.logger.error(str(e))
            return False
        else:
            return True
        
    def stop(self):
        if self.status():
            try:
                pid_file = open(self.homedir + 'motion.pid', 'r')
                pid = pid_file.read().strip('\n')
                kill(int(pid), 15)
                #remove(self.homedir + 'motion.pid')                
            except Exception as e:
                self.operations.logger.error(str(e))
                return False
            else:
                return True
        else:
            return False
        
    def status(self):
        if path.isfile(self.homedir + 'motion.pid'):
            try:
                self.pid = open(self.homedir + 'motion.pid', 'r')
            except Exception as e:
                self.operations.logger.error(str(e))
            return True
        else:
            return False
        
    def info(self):
        return "WebCam device"
    
    #Custom Functions
    
    def get_photo(self):
        snap_directory = self.config.get_custom_value('config/webcam.conf', 'General', 'snapshot_directory')
        filepath = self.homedir + snap_directory + '/lastsnap.jpg'
        try:
            f = open(filepath, 'rb')
        except Exception as e:
            self.operations.logger.error(str(e))
        else:
            return f
        
class InstallClass(object):
    def __init__(self, config_directory='config/'):
        from ConfigParser import RawConfigParser
        from os import path as ospath
        from sys import path as syspath
        #adding root directory to syspath in order to import Confreader module
        syspath.append(ospath.abspath('..'))
        from tools import Confreader
        import StringIO
        import re
        
        self.config_parser = RawConfigParser()
        self.config_directory = config_directory
        self.config = Confreader.ReadConfig(self.config_directory + 'core.conf')
        self.stringio = StringIO
        self.re = re

    def install(self):
        if not path.isfile('/etc/motion/motion.conf'):
            print 'MOTION is not installed'
            return False
        config = open('/etc/motion/motion.conf', 'r') #change to default motion config directory
        alarm_interface = raw_input('Enter name of interface which should be triggered on motion detection: ')
        width = raw_input('Enter desired image width: ')
        height = raw_input('Enter desired image height: ')
        snapshot_interval = raw_input('Enter desired snapshot interval (seconds): ')
        snapshot_directory = raw_input('Enter name of the directory where photos taken by the camera will be stored: ')
        target_dir = self.config.get_homedir() + snapshot_directory
        
        if not path.isfile(self.config_directory + 'webcam.conf'):
            try:
                self.config_parser.add_section('General')
                self.config_parser.set('General', 'snapshot_directory', snapshot_directory)
                self.config_parser.set('General', 'motion_config', 'motion.conf')
                with open(self.config_directory + 'webcam.conf', 'wb') as configfile:
                    self.config_parser.write(configfile)
            except Exception as e:
                print str(e)
                return False
        else:
            print 'WebCam module is already installed'
            return False
        
        if not path.isfile(self.config.get_homedir() + 'motion.conf'):
            result = self.re.sub('^; on_motion_detected.+', 'on_motion_detected echo \'{"alarm_interface": {"interface_name": "'\
                                                 + alarm_interface + '", "photo": "%Y%m%d%H%M%S.jpg"}}\'|nc localhost '\
                                                 + self.config.get_custom_value(self.config_directory + 'socket.conf', 'General', 'bind_port'),\
                                                 config.read(), flags=self.re.MULTILINE)
            
            result = self.re.sub('^process_id_file.+', 'process_id_file ' + self.config.get_homedir() + 'motion.pid',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^width.+', 'width ' + width,\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^height.+', 'height ' + height,\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^minimum_frame_time.+', 'minimum_frame_time 1',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^threshold .+', 'threshold 1000',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^noise_level.+', 'noise_level 96',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^snapshot_interval.+', 'snapshot_interval ' + snapshot_interval,\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^locate_motion_mode.+', 'locate_motion_mode on',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^locate_motion_style.+', 'locate_motion_style redbox',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^target_dir.+', 'target_dir ' + target_dir,\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^snapshot_filename.+', 'snapshot_filename %Y%m%d%H%M%S-snapshot',\
                                                 result, flags=self.re.MULTILINE)
            
            result = self.re.sub('^picture_filename.+', 'picture_filename %Y%m%d%H%M%S',\
                                                 result, flags=self.re.MULTILINE)
            
            config_final = open(self.config.get_homedir() + 'motion.conf', 'w')
            config_final.write(result)
        else:
            print 'Motion is already configured'
        return True
    
class InstallWebCamTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):        
        unittest.TestCase.__init__(self, methodName=methodName)
        self.webcam = InstallClass('../config/')
        
    def test_install(self):
        self.assertTrue(self.webcam.install())
        return
    
if __name__ == '__main__':
    unittest.main()