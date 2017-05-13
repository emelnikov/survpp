#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Dec 26, 2016

@author: Eugene Melnikov
'''

from threading import Thread
from telepot import Bot
from tools import Confreader
from os import mknod
from os import path
from os import remove
from subprocess import call
import urllib

class RunClass(Thread):

    def __init__(self, operations=None):
        if operations is not None:
            self.operations = operations
            self.config = Confreader.ReadConfig()
            if not path.isfile('config/telegram.conf'):
                self.operations.logger.error('Telegram interface is not installed')
                return
            else:
                self.interface_modules = operations.interface_modules
                self.device_instances = operations.device_instances
        Thread.__init__(self)
        self.daemon = True
        self.token = self.config.get_custom_value('config/telegram.conf', 'General', 'token')
        self.bot = Bot(self.token)
        self.allowed_ids = self.config.get_custom_section('config/telegram.conf', 'Allowed')
        return
        
    def run(self):
        self.bot.message_loop(self.handle)
        return True
    
    def up(self):
        if not path.isfile('config/telegram.conf'):
            self.operations.logger.error('Telegram interface is not installed')
            return
        if not path.isfile(self.config.get_homedir() + 'telegram.lock'):
            mknod(self.config.get_homedir() + 'telegram.lock')
        self.start()
        return
    
    def stop(self):
        return True
    
    def notify(self, data):
        snap_directory = self.config.get_custom_value('config/webcam.conf', 'General', 'snapshot_directory')
        filepath = self.config.get_homedir() + snap_directory + '/' + data['photo']
        for allowed_id in self.allowed_ids:
            f = open(filepath, 'rb')
            self.bot.sendMessage(allowed_id[1], u'!!!MOTION DETECTED!!!')
            self.bot.sendPhoto(allowed_id[1], f)
        return True
    
    def info(self):
        return "Telegram interface"
    
    def status(self):
        if path.isfile(self.config.get_homedir() + 'telegram.lock'):
            return True
        else:
            return False
        return False
    
    #Handle messages here
    
    def handle(self, msg):
        user_id = msg['chat']['id']
        self.operations.logger.debug(u'Received message from user with the following ID: ' + str(user_id))
        #ffmpeg test
        for i in msg:
            if i == 'voice':
                url = urllib
                file_info = self.bot.getFile(msg['voice']['file_id'])
                if path.isfile(self.config.get_homedir() + 'voice.wav'):
                    remove(self.config.get_homedir() + 'voice.wav')
                url.urlretrieve('https://api.telegram.org/file/bot' + self.token + '/'+ file_info['file_path'], self.config.get_homedir() + 'voice.oga')
                call(['ffmpeg', '-i', self.config.get_homedir() + 'voice.oga', self.config.get_homedir() + 'voice.wav'])
                call(['play', self.config.get_homedir() + 'voice.wav'])
                print msg['voice']
            
        try:
            message_body = msg['text']
        except Exception as e:
            self.operations.logger.error(str(e))
        else:
            if self.check_access(user_id):
                if len(message_body) == len('/status') and message_body[0:7] == '/status':
                    self.bot.sendMessage(user_id, self.operations.get_statuses())
                    
                elif len(message_body) == len('/stop') and message_body[0:5] == '/stop':
                    stop_result = self.operations.stop_devices()
                    if stop_result:
                        self.send_to_all(u'All devices have been disabled', user_id)
                        
                elif len(message_body) == len('/up') and message_body[0:3] == '/up':
                    run_result = self.operations.run_devices()
                    if run_result:
                        self.send_to_all(u'All devices have been enabled', user_id)
                    else:
                        self.send_to_all( u'Could not run the devices', user_id)
                        
                elif len(message_body) == len('/photo') and message_body[0:6] == '/photo':
                    photo = self.operations.device_instances['WebCam'].get_photo()
                    self.bot.sendPhoto(user_id, photo)
                    
                elif len(message_body) == len('/help') and message_body[0:5] == '/help':
                    self.bot.sendMessage(user_id, self.get_help())
                    
                elif len(message_body) == len('/alarm') and message_body[0:6] == '/alarm':
                    self.send_to_all(u'Alarm enabled', user_id)
                    self.operations.device_instances['Alarm'].play_alarm()
                    
                elif len(message_body) == len('/alarmstop') and message_body[0:10] == '/alarmstop':
                    self.send_to_all(u'Alarm disabled', user_id)
                    self.operations.device_instances['Alarm'].stop_alarm()
                    
                elif len(message_body) == len('/temp') and message_body[0:5] == '/temp':
                    self.bot.sendMessage(user_id, u"Temperature: " + str(self.operations.device_instances['Temperature'].temp) + u" C")
                    
                elif len(message_body) == len('/hum') and message_body[0:4] == '/hum':
                    self.bot.sendMessage(user_id, u"Humidity: " + str(self.operations.device_instances['Temperature'].hum) + u"%")
                    
                elif message_body[0:13] == '/startdevice ':
                    try:
                        self.operations.run_device(message_body[13:])
                    except Exception as e:
                        self.operations.logger.error(str(e))
                    if self.operations.device_instances[message_body[13:]].status():
                        self.bot.sendMessage(user_id, message_body[13:] + u" device has been started")
                    
                elif message_body[0:12] == '/stopdevice ':
                    try:
                        self.operations.stop_device(message_body[12:])
                        self.bot.sendMessage(user_id, message_body[12:] + u" device has been stopped")
                    except Exception as e:
                        self.operations.logger.error(str(e))
                        
                else:
                    self.bot.sendMessage(user_id, u'hey!')

            else:
                self.bot.sendMessage(user_id, u'Sorry, I do not know you')
            return
        
    def check_access(self, user_id):
        for aid in self.allowed_ids:
            if user_id == int(aid[1]) or int(aid[1]) == 0:
                return True
        else:
            return False
        
    def send_to_all(self, message, user_id=None):
        try:
            for aid in self.allowed_ids:
                self.bot.sendMessage(aid[1], message)
        except Exception as e:
            self.operations.logger.info(str(e) + u': ' + u'sending message by user_id...')
            self.bot.sendMessage(user_id, message)
        return
    
    def get_help(self):
        result = u"/up - start all devices\n" + \
            u"/stop - stop all devices\n" + \
            u"/status - general system status\n" + \
            u"/photo - send last photo from camera\n" + \
            u"/temp - show temperature\n" + \
            u"/hum - show humidity\n" + \
            u"/help - list of commands\n" + \
            u"/alarm - play alarm\n" + \
            u"/alarmstop - stop alarm"
        return result
            
class InstallClass(object):
    def __init__(self):
        return 
    
    def install(self):
        '''
        Installs Telegram interface.
        The function compiles config file used by the module asking user to enter bot token.
        Only one ID will be set as allowed ID - 0. Zero ID is used to allow everyone to access the bot. Access can be restricted by adding several IDs to config.
        User ID can be found in survpp.log. It is posted there all the time a message received (on DEBUG log level).
        
        Accepts: nothing
        Returns: True - if installation was successful, False - if there were any exceptions
        '''
        
        if not path.isfile('config/telegram.conf'):
            try:
                from ConfigParser import RawConfigParser
                config = RawConfigParser()
                config.add_section('General')
                token = raw_input('Enter bot token: ')
                config.set('General', 'token', token)
                config.set('General', 'sleep_value', '300')
                config.set('General', 'motion_directory', 'motion_snapshots')
                config.add_section('Allowed')
                config.set('Allowed', 'id0', '0')
                with open('config/telegram.conf', 'wb') as configfile:
                    config.write(configfile)
            except Exception as e:
                print str(e)
                return False
            print u'Telegram interface has been installed'
        else:
            print u'Telegram interface is already installed'
            return False
        return True