#!/usr/bin/python
"""
A Catch-all for some other NVP/NSX API Methods
"""

import os
import sys          # reads command-line args
import urllib       # used for url-encoding during login request
import simplejson   # converts between JSON and python objects
from api import *
from automation import nvpconfig

class ControlServices(object):
  def __init__(self, _client, log):
      self.log = log
      self.client = _client

  def get_control_cluster(self):
      self.log.info("Requesting Control Cluster Nodes")
      res_str = self.client.request("GET",
         "/ws.v1/control-cluster/node?_page_length=1000&fields=*", "")
      tzs = simplejson.loads(res_str)["results"]

      return tzs
