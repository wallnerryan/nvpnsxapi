#!/usr/bin/python
"""
Provides "transport" based functions:
    --Create / Delete:
                        -Transport Zones
                        -Transport Nodes
                        -Transport Connectors
                        
    --Verify / Check:
                        -Transport Nodes, Zones and Connectors.
"""

import os
import sys          # reads command-line args
import urllib       # used for url-encoding during login request
import simplejson   # converts between JSON and python objects
from api import *
from automation import nvpconfig

class Transport(object):
  def __init__(self, _client, log):
      self.log = log
      self.client = _client

  def get_transport_zones(self):
      self.log.info("Requesting Transport Zones")
      res_str = self.client.request("GET",
         "/ws.v1/transport-zone?fields=*", "")
      tzs = simplejson.loads(res_str)["results"]

      return tzs

  def create_transport_zone(self,tz_name):
      exists = False
      # determin if zone already exists
      res_str = self.client.request("GET","/ws.v1/transport-zone?fields=*", "") 
      for tz in simplejson.loads(res_str)["results"]: 
          if tz["display_name"] == tz_name: 
            self.log.info( "transport-zone %s already exists" % tz_name) 
            exists = True

      if exists == False:
          # create bridge transport-zone
          tz_obj = { "display_name" : tz_name } 
          res_str = self.client.request("POST","/ws.v1/transport-zone", simplejson.dumps(tz_obj)) 
          tz_uuid = simplejson.loads(res_str)["uuid"] 
          self.log.info( "created transport-zone with uuid = '%s'" % tz_uuid) 

  def delete_transport_zone(self,tz_name):
      # retrieve all transport-zones, delete if they have our display_name 
      res_str = self.client.request("GET","/ws.v1/transport-zone?fields=*", "") 
      for tz in simplejson.loads(res_str)["results"]: 
          if tz["display_name"] == tz_name: 
            self.log.info( "deleting transport-zone with uuid '%s'" % tz["uuid"]) 
            self.client.request("DELETE","/ws.v1/transport-zone/" + tz["uuid"], "")

  def create_all_transport_zones(self):
      # returns file to open
      # defaults=false gets from nvp.conf
      nvpconf = nvpconfig.NVPConfig(defaults=False)
      gconf = nvpconf.get_nvp_conf_file()
      nvp_data = open(gconf)
      config_data = simplejson.load(nvp_data)
      zones = config_data['config']['transport-zones']['zone']
      for zone in zones:
        self.create_transport_zone(zone['name'])

  # Could be useful to turn this into a generator
  # that yields the transport connectors, given they
  # are only used once, and could soak up a lot of memory
  # once the connectors become > the minimal amount for testing.
  def check_transport_connectors(self, node_name, connectors):
      res_str = self.client.request("GET","/ws.v1/transport-zone?_page_length=1000&fields=*", "")
      for connector in connectors:
        checked = 0
        for tz in simplejson.loads(res_str)["results"]:
          if tz['display_name'] == connector['name']:
              del connector['name']
              connector['transport_zone_uuid'] = tz['uuid']
              self.log.info( "valid")
              checked = 1
              break
        if checked == 0:
          self.log.info( "connector %s invalid" % connector['name'])
          exit(1)


  def check_transport_exists(self, tz_name):
      res_str = self.client.request("GET",
         "/ws.v1/transport-zone?_page_length=1000&fields=*", "")
      # Cycle through the display names returned from NVP
      for tz in simplejson.loads(res_str)["results"]:
          if tz['display_name'] == tz_name:
              self.log.info("Found Transport Zone: %s" % tz_name)
              type_found = True
              break #matched
          else:
              type_found = False

      return type_found

  def create_transport_node(self,node_info,tnode_type,
    tz_connectors,zone_forwarding,hyper,cert):
    connectors = tz_connectors

    tnode_name = node_info['name']

    if zone_forwarding != "on":
      zf = False
    else:
      zf = True

    if hyper != "true":
      hypervisor = False
    else:
      hypervisor = True

    # Determine if tnode already exists
    res_str = self.client.request("GET",
       "/ws.v1/transport-node?_page_length=1000&display_name=" \
    + tnode_name + "&fields=*", "")
    for tn in simplejson.loads(res_str)["results"]:
        if tn["display_name"] == tnode_name:
            self.log.info( "transport-node %s already exists" % tnode_name)

    # Create the transport node object
    chassis_obj = { "display_name" : tnode_name, 
                    "integration_bridge_id" : "",
                    "zone_forwarding" : zf,
                    "admin_status_enabled": bool(1), #Default
                    "mgmt_rendezvous_client": bool(0), #Default
                    "mgmt_rendezvous_server": bool(0), #Default
                    "tunnel_probe_random_vlan": bool(1), #Default
                    "tags":[],
                    "credential": {
                         "client_certificate": {
                               "pem_encoded": cert
                         },
                         "type": "SecurityCertificateCredential"
                    },
                    "transport_connectors" : tz_connectors
                  }

    if hypervisor == True:
      chassis_obj["integration_bridge_id"] = "br-int"

    if tnode_type == "COMPUTE":
      pass

    # Rendezvous Server Settings needed on SERVICE or GATEWAY
    # depending on the setup. i.e. Remote Gateways need to
    # act as Client.
    if tnode_type == "SERVICE":
       if node_info['mgmt_rendezvous_server'] == "false":
          chassis_obj["mgmt_rendezvous_server"] = bool(0)

       elif node_info['mgmt_rendezvous_server'] == "true":
          chassis_obj["mgmt_rendezvous_server"] = bool(1)

    if tnode_type == "GATEWAY":
       if node_info['mgmt_rendezvous_client'] == "false":
          chassis_obj["mgmt_rendezvous_client"] = bool(0)

       elif node_info['mgmt_rendezvous_client'] == "true":
          chassis_obj["mgmt_rendezvous_client"] = bool(1)

    #Send the json POST
    res_str = self.client.request("POST","/ws.v1/transport-node",
       simplejson.dumps(chassis_obj))
    chassis_uuid = simplejson.loads(res_str)["uuid"]
    self.log.info( "Created edge device with uuid = '%s'" % chassis_uuid)

  #Delete the transport node
  # 
  # @param tnode_name "name of the trasnport-node"
  # 
  def delete_transport_node(self,tnode_name):
    # Get Transport Node UUID
    res_str = self.client.request("GET", "/ws.v1/transport-node?_page_length=1000&fields=*", "")
    for transport_node in simplejson.loads(res_str)['results']:
      if transport_node['display_name'] == tnode_name:
        tnode_uuid = transport_node['uuid']
        res_str = self.client.request("DELETE",
           "/ws.v1/transport-node/%s" % tnode_uuid, "")
        break

  #Does this node exist?
  #
  #
  def tnode_exists(self,tnode):
    found = False
    res_str = self.client.request(
        "GET","/ws.v1/transport-node?_page_length=1000&display_name=" +
        tnode + "&fields=*", "")
    for node in simplejson.loads(res_str)["results"]: 
      if node["display_name"] == tnode: 
        self.log.info("Found Transport Node %s" % tnode)
        found = True
    if not found:
       self.log.debug("Transport Node Not Found: %s" % tnode)
    return found

  #Takes in a list of connectors and
  #verifies the zone exists for each connector
  #
  #
  def verified_zones(self,connectors):
    verified = True
    for zone in connectors:
      zone_found = self.check_transport_exists(zone['name'])
      if zone_found == False:
        verified = False
        self.log.info( "Transport Zone %s defined in doesn't exist on nvp server" % zone['name'])

    return verified

  def get_tnode_uuid(self,tnode_name):
    found = 0
    res_str = self.client.request("GET","/ws.v1/transport-node?display_name="\
                           + tnode_name + "&fields=*&_page_length=1000", "")
    for tnode in simplejson.loads(res_str)['results']:
      if tnode['display_name'] == tnode_name:
        tnode_uuid = tnode['uuid']
        found = 1
        break

    if found == 0:
      self.log.info( "Node %s not found" % tnode_name)
      exit(1)
    else:
      return tnode_uuid

  def get_interface_statistics(self, uuid, eth):
    self.log.info("Requesting Statistics")
    res_str = self.client.request("GET",
       "/ws.v1/transport-node/%s/interface/%s/statistic" %
       (uuid, eth), "")
    stats = simplejson.loads(res_str)
    return stats


