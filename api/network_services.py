#!/usr/bin/python
"""
Used for NVP L3 Services such as:
    --Create / Delete a Logical Router
    --Create / Delete Logical Router NAT Rules
    --Create / Delete an L3 Gateway Service
"""

import os
import sys          # reads command-line args
import urllib       # used for url-encoding during login request
import simplejson   # converts between JSON and python objects
import ConfigParser
import api
from transport import *

class NetworkServices(object):
  def __init__(self, _client, log):
      self.log = log
      self.client = _client

  #ROUTERS

  # Create a logical router
  # @param lrouter_name  "name of the router"
  # @param default_route "default "gateway" router ip address" 
  def create_lrouter(self,lrouter_name, default_route):

    # determine if lrouter already exists
    res_str = self.client.request("GET","/ws.v1/lrouter?display_name="\
                             + lrouter_name + "&fields=*&_page_length=1000", "")
    for lrouter in simplejson.loads(res_str)["results"]:
        if lrouter["display_name"] == lrouter_name:
            self.log.debug( "lrouter %s already exists" % lrouter_name)
            exit(1)

    # create lrouter
    lrouter_obj = {
    "display_name": lrouter_name, 
    "distributed": False, #eventually should be passed in from json
    "nat_synchronization_enabled": True, #eventually should be passed in from json
    "routing_config": {
      "default_route_next_hop": {
        "gateway_ip_address": default_route, 
        "type": "RouterNextHop"
      }, 
      "type": "SingleDefaultRouteImplicitRoutingConfig"
    }, 
    "type": "LogicalRouterConfig"
                  }

    res_str = self.client.request("POST","/ws.v1/lrouter", simplejson.dumps(lrouter_obj))
    lrouter_uuid = simplejson.loads(res_str)["uuid"]
    self.log.debug( "created logical router with uuid = '%s'" % lrouter_uuid)

  # @def Delete the lrouter
  # @param lrouter_name "name of the logical router"
  def delete_lrouter(self,lrouter_name):
    lrouter_uuid = self.get_router_uuid(lrouter_name)
    res_str = self.client.request("DELETE", "/ws.v1/lrouter/%s" % lrouter_uuid, "")
    self.log.debug( "Deleted router('%s') with uuid %s" % (lrouter_name,lrouter_uuid))

  # @def    Create a logical router port
  # @param  lrouter_name      "name of router"
  # @param  lrouter_port_name "port name"
  # @param  lrouter_port_ip   "port ip address"
  # @param  lrouter_port_mac  "port mac address"
  def create_lrouter_port(self,lrouter_name, lrouter_port_name, lrouter_port_ips):

    lrouter_uuid = self.get_router_uuid(lrouter_name)

    # create lrouter
    lrouter_port_obj = {
      "display_name": lrouter_port_name, 
      "admin_status_enabled": True, 
      "ip_addresses": lrouter_port_ips
      , 
      "type": "LogicalRouterPortConfig"
                  }

    res_str = self.client.request("POST","/ws.v1/lrouter/" + lrouter_uuid +\
                             "/lport" , simplejson.dumps(lrouter_port_obj))
    lrouter_port_uuid = simplejson.loads(res_str)["uuid"]
    self.log.debug( "created logical router port with uuid = '%s'" % lrouter_port_uuid)

  #Create a router attachment, used in create_lrouter_port_attachment
  #
  #@param type  "L3Gateway|Patch"  (more can be supported, just not done yet)
  #@param port
  #@keyparams
  #           Type:         Need:
  #               Patch:      switch= and peer=
  #               L3Gatway:   l3_gws= vlan=
  #

  def get_lswitch_uuid(lswitch_name):
     ls_uuid = None
     found = False
     res_str = self.client.request("GET","/ws.v1/lswitch?fields=*", "") 
     for ls in simplejson.loads(res_str)["results"]: 
         if ls["display_name"] == lswitch_name: 
           found = True
           ls_uuid = ls['uuid']
           break
     if found == False:
        self.log.debug( "logical switch not found") 
        exit(1)
    
     return ls_uuid

  def get_lport_uuid(lswitch_name,lport_name):
     lp_uuid = None
     found = False
     lswitch_uuid = self.get_lswitch_uuid(lswitch_name)
     url = "/ws.v1/lswitch/" + lswitch_uuid
     res_str = self.client.request("GET",url + "/lport?fields=*", "") 
     for lp in simplejson.loads(res_str)["results"]: 
        if lp["display_name"] == lport_name:
            lp_uuid = lp['uuid']
            found = True
            break
     if found == False:
        self.log.debug( "logical port not found")
        exit(1)
    
     return lp_uuid

  def create_router_attachment(self,type, port, **kwargs):
    params = kwargs

    if type == "Patch":
      try:
        peer_port_uuid = self.get_lport_uuid(params['switch'],params['peer'])
      except KeyError as e:
        self.log.debug(e)
        exit(1)

      patch = {
        "peer_port_uuid": peer_port_uuid,
        "type": "PatchAttachment"
      }
      return patch

    elif type == "L3Gateway":
      try:
        l3gws_uuid = self.get_gws_uuid(params['l3_gws'])
        vlan = params['vlan']
      except KeyError as e:
          self.log.debug(e)
          exit(1)

      l3gwa = {
        "l3_gateway_service_uuid": l3gws_uuid,
        "vlan_id": vlan,
        "type": "L3GatewayAttachment"
      }
      return l3gwa

    #!#####################################!  
    #!# Can Support more attachment types #!
    #!#####################################!
    else:
      self.log.debug( "Attachment type not recognized")

  # @def create_lrouter_port_attachment
  # @param lrouter_name
  # @param attachment
  # Takes in an attachment object of any type
  # and creates the attachment on the given port
  # @type , @port are needed from object.
  def create_lrouter_port_attachment(self,lrouter_name, port, attachment):
    lrouter_uuid = self.get_router_uuid(lrouter_name)
    lrp_uuid = self.get_router_port_uuid(lrouter_name,port)

    res_str = self.client.request("PUT","/ws.v1/lrouter/" + lrouter_uuid +\
       "/lport/"+ lrp_uuid +"/attachment" , simplejson.dumps(attachment))
    self.log.debug( "Created logical router port "+
       "attachment on port %s with uuid = '%s'" % (port, lrp_uuid))


  # @def   Delete the lrouter port
  # @param lrouter_name      "name of the lrouter"
  # @param lrouter_port_name "name of port"
  def delete_lrouter_port(self,lrouter_name, lrouter_port_name):

    lrouter_uuid = self.get_router_uuid(lrouter_name)

    res_str = self.client.request("GET","/ws.v1/lrouter/" + lrouter_uuid + "/lport?display_name="\
                             + lrouter_port_name + "&fields=*&_page_length=1000", "")
    for lr_port in simplejson.loads(res_str)['results']:
      if lr_port ['display_name'] == lrouter_port_name:
        lrouter_port_uuid = lr_port['uuid']
        res_str = self.client.request("DELETE", "/ws.v1/lrouter/" + lrouter_uuid + "\
                                 /lport/" + lrouter_port_uuid , "")
        break

  #Reusable method @def get_router_uuid()
  # @param lrouter_name     "logical router name"
  # @return lrouter_uuid "UUID of router"
  # 
  def get_router_uuid(self,lrouter_name):
    found = 0
    res_str = self.client.request("GET","/ws.v1/lrouter?display_name="\
                             + lrouter_name + "&fields=*&_page_length=1000", "")
    for lrouter in simplejson.loads(res_str)['results']:
      if lrouter['display_name'] == lrouter_name:
        lrouter_uuid = lrouter['uuid']
        found = 1
        break

    if found == 0:
      raise NameError("Router %s\not found" % lrouter_name)

    else:
      return lrouter_uuid

  # @def get_router_port_uuid
  # @param lrouter_name
  # @param lrport_name "Logical Router Port name"
  # 
  # @return logical router port UUID
  def get_router_port_uuid(self,lrouter_name,lrport_name):
    found = 0
    lrouter_uuid = self.get_router_uuid(lrouter_name)
    res_str = self.client.request("GET","/ws.v1/lrouter/" + lrouter_uuid +\
                             "/lport?fields=*&_page_length=1000", "")
    for port in simplejson.loads(res_str)['results']:
      if lrport_name == port["display_name"]:
        lrport_uuid = port['uuid']
        found = 1
        break

    if found == 0:
      raise NameError("Router port %s\not found" % lrport_name)

    else:
      return lrport_uuid

  #END ROUTERS

  #NAT

  # @def create a logical NAT rule
  # @param lrouter_name   "name of the logical router"
  # @param type           "dest, src, nosrc, nodst"
  # @param match          "match tuple"
  # @param order          "relative priority, lower = evaluated 1st"
  #
  # @keyparams            "keyword arguments for NAT rules"
  #         If Making a Destination NAT Rule
  #               Required: to_dest_ip    "destination ip address"
  #               Optional: to_dest_port   "destination port"
  #
  #         If Making a Source NAT Rule
  #               Required: to_src_ip_max "source ip address max"
  #               Required: to_src_ip_min "source ip address min"
  #               Optional: to_src_port   "source port"
  #
  def create_nat(self,lrouter_name, type, match, order=255, **kwargs):
    params = kwargs

    nat_obj = {
        "match": match,
        "order": order, 
    }

    #SourceNatRule
    if type == "DestinationNatRule":
      try:
        nat_obj.update({
          "to_destination_ip_address": params['to_dest_ip'], 
          "type": "DestinationNatRule"
          })
      except KeyError as e:
        self.log.debug(e)
        exit(1)

      #Optional Param
      if "to_dest_port" in kwargs.keys():
        try:
         nat_obj.update({"to_destination_port": params['to_dest_port']})
        except KeyError as e:
          self.log.debug(e)
          exit(1)

    #DestinationNatRule  
    elif type == "SourceNatRule":
      try:
        nat_obj.update({
          "to_source_ip_address_min": params['to_src_ip_min'], 
          "to_source_ip_address_max": params['to_src_ip_max'], 
          "type": "SourceNatRule"
         })
      except KeyError as e:
        self.log.debug(e)
        exit(1)

      #Optional Param
      if "to_src_port" in kwargs.keys():
        try:
         nat_obj.update({"to_source_port": params['to_src_port']})
        except KeyError as e:
          self.log.debug(e)
          exit(1)
    #NoSourceNatRule
    elif type == "NoSourceNatRule":
        nat_obj.update({
          "type": "NoSourceNatRule"
         })

    #NoDestinationNatRule
    elif type == "NoDestinationNatRule":
      nat_obj.update({
          "type": "NoDestinationNatRule"
         })

    else:
      self.log.debug( "[type] %s of NAT is not recognized" % type)
      exit(1)

    #try and retreive the router uuid
    lrouter_uuid = self.get_router_uuid(lrouter_name)
    res_str = self.client.request("POST","/ws.v1/lrouter/" + lrouter_uuid + "/nat",\
                             simplejson.dumps(nat_obj))
    nat_rule_uuid = simplejson.loads(res_str)["uuid"]
    self.log.debug( "Created logical router NAT Rule with uuid = '%s'" % nat_rule_uuid)

  # @def create a logical NAT match dict
  # Required: @param eth_type "ethernet type number"
  # Optional: @keyparams src_adds, dst_adds, proto, src_port, dst_port
  def create_nat_match(self,eth_type, **kwargs):
    match = { 
        "ethertype": eth_type
     }
    # All these keys below are options,
    # Therefore we dont have to throw a KeyError
    for key, value in kwargs.items():
        if key == "src_adds":
          match.update({"source_ip_addresses": value})
        elif key == "dst_adds":
          match.update({"destination_ip_addresses":value})
        elif key == "proto":
          match.update({"protocol":value})
        elif key == "src_port":
          match.update({"source_port":value})
        elif key == "dst_port":
          match.update({"destination_port":value})

    return match


  # @def delete NAT rule
  # @param lrouater_name  "name or logical router" 
  # @param nat_uuid       "uuid of nat rule"
  def delete_nat(self,lrouter_name, nat_uuid):
    #Get router UUID
    lrouter_uuid = self.get_router_uuid(lrouter_name)
    res_str = self.client.request("DELETE", "/ws.v1/lrouter/"+ lrouter_uuid +\
                             "/nat/%s" % nat_uuid, "")
    self.log.debug( "Deleted NAT Rule with uuid = '%s'" % nat_uuid)

  #TODO
  def update_nat(self):
    self.log.debug( "method not implemented :) ")
    raise NotImplementedError

  #Gets a NAT rule based on lrouter
  #and NAT Rule Criteria
  def get_nat_rule(self):
    pass

  # Used to output NAT rules
  # based on a given Logical Router
  #
  # @see NVP API, no names are given to
  # to NAT Rules in 3.0.0, so we need
  # a way to list the UUIDs in order
  # to delete them.
  def print_nat_rules(self,lrouter_name):
    #Get router UUID
    lrouter_uuid = self.get_router_uuid(lrouter_name)
    res_str = self.client.request("GET", "/ws.v1/lrouter/" + lrouter_uuid +\
                             "/nat?fields=*&_page_length=1000", "")
    nat_rules = simplejson.loads(res_str)["results"]
    for nat_rule in nat_rules:
      self.log.debug( """
            Type:  %s
            Order: %s
            Match: %s
            UUID:  %s
            Full-Result: %s

            """ % (nat_rule["type"],nat_rule["order"],\
                   nat_rule["match"],nat_rule["uuid"],nat_rule))


  #END NAT


  #GATEWAY SERVICES

  # @def Create a Gateway Service
  # @param gw_name  "name of the gateway service"
  # @param type     "L2"|"L3"|"Domain" Note: L3 Gateway is "Experimental" in 3.0.0
  # @param gateways "List of gateways for this gateway service"
  def create_gw_service(self,gws_name, type, gateways=None):

    if type == "L2":
      gws_type = "L2GatewayServiceConfig"

    elif type == "L3":
      gws_type = "L3GatewayServiceConfig"

    elif type == "Domain":
      gws_type = "DomainGatewayServiceConfig"

    _gw = {
    "display_name": gws_name, 
    "gateways": [gateways], 
    "type": gws_type
    }

    res_str = self.client.request("POST","/ws.v1/gateway-service", simplejson.dumps(_gw))
    gw_service_uuid = simplejson.loads(res_str)["uuid"]
    self.log.debug( "Created gateway service with uuid = '%s'" % gw_service_uuid)

  #@def Create L2 Gateway
  #@param gw_name
  #@param d_id   "device id"
  def create_l2_gateway(self,gw_name,d_id):

    gw_uuid = get_tnode_uuid(gw_name)

    l2gw = {
        "transport_node_uuid": gw_uuid, 
        "device_id": d_id, 
        "type": "L2Gateway"
      }
    return l2gw

  #@def Create L3 Gateway
  #@param d_id  "device id"
  #@param g_id  "group id"
  def create_l3_gateway(self,gw_name, d_id, g_id):

    gw_uuid = get_tnode_uuid(gw_name)

    l3gw = {
        "transport_node_uuid": gw_uuid, 
        "device_id": d_id, 
        "group_id": g_id, 
        "type": "L3Gateway"
      }
    return l3gw

  # @def Create Domain Gateway
  # @param gw_name
  # @param remote_ip   "remote gateway ip address"
  # @param tunnel_type "stt, gre, ip_sec" etc.
  def create_domain_gw(self,gw_name, remote_ip, tunnel_type):

    gw_uuid = get_tnode_uuid(gw_name)

    domain_gw = {
        "local_transport_zone": gw_uuid, 
        "remote_ip_address": remote_ip, 
        "tunnel_type": tunnel_type, 
        "type": "DomainGateway"
      }
    return domain_gw

  # See if gw service exists
  # @param gws_name "Gateway Service name"
  def gw_service_exists(self,gws_name):
    exists = False
    res_str = self.client.request("GET","/ws.v1/gateway-service?"\
                             "&fields=*&_page_length=1000", "")
    for gw_service in simplejson.loads(res_str)["results"]:
        if gw_service["display_name"] == gws_name:
           exists = True

    return exists

  # Delete a gateway service
  # @param gws_name   "Gateway Service name"
  def delete_gw_service(self,gws_name):
    gws_uuid = self.get_gws_uuid(gws_name)
    res_str = self.client.request("DELETE", "/ws.v1/gateway-service/%s" % gws_uuid, "")

  #TODO
  def update_gw_service(self):
    self.log.debug( "method not implemented :) ")
    raise NotImplementedError()

  def get_gws_uuid(self,gws_name):
    found = 0
    res_str = self.client.request("GET","/ws.v1/gateway-service?"\
                             "fields=*&_page_length=1000", "")
    for gw_service in simplejson.loads(res_str)['results']:
      if gw_service['display_name'] == gws_name:
        gws_uuid = gw_service['uuid']
        found = 1
        break

    if found == 0:
      self.log.debug( "Gateway Service %s not found" % gws_name)
      exit(1)
    else:
      return gws_uuid


  #END GATEWAY SERVICES

