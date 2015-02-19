#!/usr/bin/python
"""
NVPConfig
    Interacts with nvp json and conf file. You can pull a
    specific node's information and or controller's information
    from the json file.

USE:
 nvpconfig provides a layer to interact with
 the nvp.conf file and the nvp json configuration.

 1. By default nvp-config.json is looked for in /etc/nvp/configs/

 2. If defaults is set to False, it looks at nvp.conf in /etc/nvp/
 for relevent information, there is an example nvp.conf in the package root.

 3. Or dont specify defaults, and give this class a full path to the
 config file using configfile=<file/path/config-example.json>

"""

import os
import logging
import sys          # reads command-line args
import simplejson   # converts between JSON and python objects
import ConfigParser

class NVPConfig(object):
    "Interaction layer for global NVP configuration file"
    
    def __init__(self,**kwargs):
        #Defaults
        self.defaults = None
        self.configfile = None
        self.configloc = "/etc/nvp/configs"                               
        self.configname = "nvp-config.json"                     
        self.conf = "%s/%s" % (self.configloc, self.configname) 
        self.key = "ovsclient-cert.pem"
        self.nvp_config_data = {}
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        dirs = "/etc/nvp/automation/configs"
        try:
          os.makedirs(dirs)
        except OSError:
          if os.path.exists(dirs):
              pass
          else:
              raise
        
        if self.defaults == True:    
            try:
                self.load_nvp_data(self.conf)
            except KeyError:
                print "Could not load NVP data"
        elif self.defaults == False:
	    #fetches from nvp.conf
            try:
		self.get_conf_loc()
		self.get_conf_name()
                self.load_nvp_data(self.conf)
            except KeyError:
                print "Could not load NVP data"
        elif self.defaults == None:
            #fetches from passed in configfile path
            try:
                self.load_nvp_data(self.configfile)
            except KeyError:
                print "Could not load NVP data"
        else:
            #defaults = None, must call load_nvp_data(data)
            pass
        
        
    def set_conf(self,conf_file):
        self.conf = conf_file
    
    def set_key(self,pem):
        self.key = pem
        
    def set_nvp_config_data(self,data):
        self.nvp_config_data = data

    def reset_conf(self):
        #re configures conf file after gets
	self.conf = "%s/%s" % (self.configloc, self.configname)
        
    def get_nvp_user(self):
        _usr = None
        try:
      	  config = ConfigParser.RawConfigParser()
      	  config.read("/etc/nvp/nvp.conf")
          _usr = config.get('nvp-controller', 'user')
        except ValueError as e:
          print "nvp.conf file error"
          print e
          exit(1)
        return _usr
    
    def get_nvp_pass(self):
        _pass = None
        try:
      	  config = ConfigParser.RawConfigParser()
      	  config.read("/etc/nvp/nvp.conf")
          _pass = config.get('nvp-controller', 'password')
        except ValueError as e:
          print "nvp.conf file error"
          print e
          exit(1)
        return _pass

    def get_conf_loc(self):
        if os.path.exists("/etc/nvp/nvp.conf"):
	 try:
      	  config = ConfigParser.RawConfigParser()
      	  config.read("/etc/nvp/nvp.conf")
	  full_path = config.get('nvp-controller', 'config-file')
          head, tail = os.path.split(full_path)
          self.configloc = head
	  self.reset_conf()
         except ValueError:
          print "nvp.conf file error"
          exit(1)
        else:
	 print "/etc/nvp/nvp.conf does not exists"
	 exit(1)

    def get_conf_name(self):
        try:
          config = ConfigParser.RawConfigParser()
          config.read("/etc/nvp/nvp.conf")
          full_path = config.get('nvp-controller', 'config-file')
          head, tail = os.path.split(full_path)
	  self.configname = tail
	  self.reset_conf()
        except ValueError:
          print "nvp.conf file error"
          exit(1)
    
    def get_snapshot_loc(self):
        try:
          config = ConfigParser.RawConfigParser()
          config.read("/etc/nvp/nvp.conf")
          full_path = config.get('nvp-controller', 'snapshot-location')
        except ValueError:
          print "nvp.conf file error"
          exit(1)
        return full_path

    def get_nvp_conf_file(self):
	return self.conf
        
    def load_nvp_data(self, data=None):
        #Load NVP Data
        if data == None:
            data = self.conf
            
        if os.path.exists(data):
          nvp_data = open(data)
          config_data = simplejson.load(nvp_data)
          self.set_nvp_config_data(config_data)
    	else:
	  print "%s does not exist" % data
	  exit(1)

    def get_node_info(self,tnode_name):
        #Return a dict of specified node info
        found = False
        tnode = None
	try:
         nodes = self.nvp_config_data['config']['transport-nodes']['node']
         for node in nodes:
          if tnode_name == node['name']:
            tnode = node
	    found = True
            break;
	 if not found:
	   #Node missing in config file
	   raise Exception("NodeNotFoundException")
	#Missing key is found can cause err
	except KeyError as e:
	  print e
		
        return tnode
        
    def get_controller_info(self):
        c_info = {}
        c_info['ip'] = self.nvp_config_data['config']['nvp']['ip']
        
        return c_info

    def get_router_info(self,router_name):
        #Return a dict of specified node info
        lrouter = None
        found = False
	try:
         routers = self.nvp_config_data['config']['routers']['router']
         for router in routers:
          if router_name == router['name']:
            lrouter = router
	    found = True
            break;
	 if not found:
	   #router missing in config file
	   raise Exception("RouterNotFoundException")
	#Missing key is found can cause err
	except KeyError as e:
	  print e
		
        return lrouter
    
    def get_gws_info(self,gws_name):
        #Return a dict of specified node info
        found = False
        gw_service = None
	try:
         services = self.nvp_config_data['config']['gateway-services']['service']
         for service in services:
          if gws_name == service['name']:
            gw_service = service
	    found = True
            break;
	 if not found:
	   #router missing in config file
	   raise Exception("GatewayServiceNotFoundException")
	#Missing key is found can cause err
	except KeyError as e:
	  print e
		
        return gw_service
    
    def get_nat_info(self,nat_name):
        #Return a dict of specified node info
        found = False
        nat_rule = None
	try:
         rules = self.nvp_config_data['config']['nat']['rules']
         for rule in rules:
          if nat_name == rule['name']:
            nat_rule = rule
	    found = True
            break;
	 if not found:
	   #router missing in config file
	   raise Exception("NatRuleNotFoundException")
	#Missing key is found can cause err
	except KeyError as e:
	  print e
		
        return nat_rule
    
