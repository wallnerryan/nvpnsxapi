#!/usr/bin/python
"""
A script to create/delete transport nodes in NVP.

    -Hypervisor Node
    -Gateway Node
    -Service node
    
"""

import os
import os.path
import commands
import sys          # reads command-line args
import urllib       # used for url-encoding during login request
import simplejson   # converts between JSON and python objects
import ConfigParser # used to parse the transport zone config file
import re           # used to parse the certificate stored in ovsclient-cert.pem
import nvpconfig
from common.util import *
from api.ovs import *
from api.ovs_rmt import *
from api import nvp2
from common.util import ssh as remote_ssh
from api.nvp_api import NVPApi

def main():
    #Possibly cleaner with docopt
    #check/get command line arguments
    if len(sys.argv) != 3: 
        print "usage: %s <create|delete> <transport node>" % sys.argv[0]
        exit(1) 
    
    #Assign passed arguments to local variables
    _cmd = sys.argv[1] 
    _tnode_name = sys.argv[2]
  
    api = NVPApi()
    # Initialize variables from values stored in config file
    infoutil = nvpconfig.NVPConfig(defaults=False)
    tnode_info = infoutil.get_node_info(_tnode_name)
    controller_info = infoutil.get_controller_info()
    
    #assign needed variables
    controller_ip = controller_info['ip']
    tnode_type = tnode_info['type']
    management_addr = tnode_info['management-address']
    integration_bridge_id = tnode_info['integration-bridge']
    tnode_name = tnode_info['name']
    connectors = tnode_info['connectors']
    interface = tnode_info['data-network-interface']
    
    #login to NVP to make REST calls
    helper = nvp2.NVPClient()
    helper.login()
  
    if _cmd == "create":
        api.create_all_transport_zones() #why do this everytime a create tn is called?
	
	# Determine if node already exists
	if(api.tnode_exists(_tnode_name)):
	    print "Node already exists"
	    exit()
        #Determine if transport zone exists in cluster		
	if not (api.verified_zones(tnode_info['connectors'])):
	    print "Zone Not Found"
	    exit()
	    
        # ----Create Transport Node---/
	if tnode_type == "COMPUTE":
	  rmt = tnode_info['remote']
	  s = None
	  if rmt:
	    user = raw_input("Username for %s?: " % management_addr)
	    password = raw_input("Password for %s@%s?: " % (user,management_addr))
	    s = remote_ssh.ssh_client(management_addr,22,user,password)  
          #Verify OVS is setup
	  if rmt:
	    cert = remote_ovs_init(s,controller_ip,interface)
	  else:
	    cert = ovs_init(controller_ip,interface)
          #Return the formatted connectors
          api.check_transport_connectors(tnode_name, connectors)
          #Create the transport node
          api.create_transport_node(tnode_info,tnode_type,connectors,"off","true",cert)

	elif tnode_type == "SERVICE":
	  #TODO - is this node the address?
	  cert = get_manager_cert(controller_ip)
          #Return the formatted connectors
          api.check_transport_connectors(tnode_name, connectors)
          #Create the transport node
          api.create_transport_node(tnode_info,tnode_type,connectors,"on","false",cert)

	elif tnode_type == "GATEWAY":
	  #TODO - is this node the address?  
	  cert = get_manager_cert(controller_ip)
          #Return the formatted connectors
          api.check_transport_connectors(tnode_name, connectors)
          #Create the transport node
          api.create_transport_node(tnode_info,tnode_type,connectors,"off","false",cert)
	    
    elif _cmd == "delete":
        api.delete_transport_node(tnode_name)
    else: 
        print "unknown command '%s'" % _cmd

if __name__ == "__main__":
    main()
