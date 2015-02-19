#!/usr/bin/python
"""
nvp2.py

An HTTP layer to communicate with the NVP Control Cluster

Provides:
          -Login
          -HTTP Requests
          -Output HTTP Responses
          -Basic Cookie Mgmt.
          
USE:
  1. If you pass in nothing, defaults are loaded. /etc/nvp/nvp.conf
  is used to get NVP IP, Username, Password, and Port
  
  2. If config is set to false, you must at-least call set_ip() before
  you call login.

  3. You can also call set_port, set_uname, set_pw, set_conf to
  modify what information the connection class uses.
  
"""

import sys          # reads command-line args
import httplib      # basic HTTP library for HTTPS connections
import urllib       # used for url-encoding during login request
import simplejson   # converts between JSON and python objects
import ConfigParser

# Helper class to do basic login, cookie management, and provide base
# method to send HTTP requests.
class NVPClient(object):
  """NVP Connection Class"""
  # Used to share login state to subclasses
  __shared_state = {}
  def __init__(self,**kwargs):
    self.__dict__ = self.__shared_state #for object login inheritence.
    #Default Values
    self.config = True                  #False to use constructors
    self.conf = "/etc/nvp/nvp.conf"     #default
    self.uname = "admin"                #backward compat with nvp.py 
    self.pw = "admin"
    self.port = 443
    self.ip = None
    for key, value in kwargs.items():
      setattr(self, key, value)
      
  #setters and getters
  def set_ip(self,ip):
    self.ip = ip

  def set_port(self,port):
    self.port = port

  def set_uname(self,usr):
    self.uname = usr

  def set_pw(self,passw):
    self.pw = passw

  def set_conf(self,nvp_file):
    self.conf = nvp_file

  #private, used to load nvp config file
  def _load_conf(self,file):
    try:
      p = ConfigParser.RawConfigParser()
      p.read(file)
      self.ip = p.get('nvp-controller', 'ip')
      self.port = p.get('nvp-controller', 'port')
      self.uname = p.get('nvp-controller', 'user')
      self.pw = p.get('nvp-controller', 'password')
    except ValueError:
      print "nvp-config file parse exception!"

  #login to NVP Controller
  def login(self):
    # Check to see if config was given, load it
    # Or load defaults if not specified.
    # Unless config==False
    if self.config:
      try:
        self._load_conf(self.conf)
      except ValueError:
        print """Could not load config. Default is \
        %s\%s""" % (os.getcwd(),self.conf)
        
    if self.ip == None:
        raise Exception("No Valid IP Address")
    
    else:
      try:
        #Create connection and login
        self.httpcon = httplib.HTTPSConnection(self.ip,self.port)
        self.httpcon.connect()
      except IOError:
        print "Could not connect, need valid IP"
        exit()

    headers = {}
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    body = urllib.urlencode({ "username": self.uname, "password": self.pw })
    self.httpcon.request("POST", "/ws.v1/login", body, headers)
    response = self.httpcon.getresponse()
    self.cookie = response.getheader("Set-Cookie", "")
    if response.status != httplib.OK:
        raise Exception("Login Failed")
    self.httpcon.close()

  #Basic Request Method 
  def request(self, method, url, body, content_type="application/json"):
    headers = { "Content-Type" : content_type, "Cookie" : self.cookie }
    self.httpcon.request(method, url, body, headers)
    response = self.httpcon.getresponse()
    self.cookie = response.getheader("Set-Cookie", self.cookie)
    r_contenttype = response.getheader("content-type")
    status = response.status
    if status != httplib.OK and status != httplib.CREATED and status != httplib.NO_CONTENT:
      print "%s to %s got unexpected response code: %d (content = '%s')" \
          % (method,url, response.status, response.read())
      return None
    if r_contenttype == "application/octet-stream":
      #for snapshots
      return response
    else:
      return response.read()
