# SURVPP

SURVPP is module-based home control system. written on Python.

The SURVPP system uses two packages to dynamically load modules from them:  

***Modules***: in source code it is often called 'Devices'. This package is used to connect some things you would like to control in your home. It can be modules for surveillance cameras, door sensors, home alarm and so on. In other words, device modules, are python modules which control or retrieve information from some external devices or services.  
***Interfaces***: modules from this package are used to provide user with possibility to interact with the system - directly (e.g., command-line or socket interface) or via some external services (e.g., chats).  

Modules from these packages should contain the following classes and functions, in order to be loaded and lauched successfully:  

* ***InstallClass*** - class which loads during system installation process. This class is not obligatory and can be absent in the module if it does not require any preliminary actions in order to be started.  
	* ***install()*** - function which is called during installation process. Usually it is responsible for config files creation or installation of some third-party software required by the module.  

* ***RunClass*** - class which loads on module start.
	* ***up()*** - function which starts device or interface. It usually either starts a thread which communicates with some external service (e.g., messenger) or starts some third-party software (e.g., "motion", like WebCam module does).
	* ***stop()*** - stops the module. It should either, for example, create conditions which termiate running thread of the module or stop some third-party software which was started by the up() function before.
	* ***status()*** - provides status of the module. Returns **True** if module is running and **False** if it is not.
	* ***notify()*** - this function is used in **Interface** modules only. It can be called by some device in order to notify user via this interface about any event.
	* ***info()*** - provides information about the module. It can be its name and any infromation you think is important to know.
## Installation
In order to work with WebCam module, `motion` should be installed.
```
$ sudo apt-get install motion
```
In order to install SURVPP, `run.py` with key `install` should be launched. Follow instructions in terminal to complete installation.
```
$ python run.py install
```
After installation you may want to customize configuration files created in `survpp/config`.
## Usage
To use SURVPP, run main script `run.py` wihout keys.
```
$ python run.py
```
If there are any issues, you can check `survpp.log` located in home directory (it is scpecified in `core.conf`) for errors and notifications. Logging level is also specified in `core.conf`.
In order to get your Telegram user/group ID, you should set loggin level to DEBUG (10), run SURVPP and write a message to your bot. ID will be written to `survpp.log`.

## Config file(s) explanation
### core.conf
***[General]***  
**homedir** - path to directory where locks and logs of the project will be stored. SURVPP stores almost everything (except configs) in this directory.  
***[Devices]***  
List of device modules. Installation process puts all modules from 'Modules' package to this section. It is possible to disable a device by commenting ot out in the config.  
***[Obligatory Devices]***  
List of devices which should be started in any case once the system is launched. Non-obligatory modules are started according to their status before system restart. If non-obligatory module was not active and the system was then restarted, it will not become enabled. Obligatory device will start even if it was inactive before restart.  
***[Interfaces]***  
List of interface modules. It is automatically filled in by installation process by all modules from 'Interfaces' package.  
***[Obligatory Interfaces]***  
The same as obligatory devices. The only difference is that obligatory interface cannot be turned of from any other interface. In other words - it is always up and running.  
***[Logger]***  
Settings related to logging.  
**logfile** - name of main log file. By default it is set to 'survpp.log' during installation process.  
**level** - logging level. Should be a number. Explanation of the levels is available in the config file.  