#!/usr/bin/python
'''
Test Script for API
'''

from api.nvp_api import NVPApi

#Instantiate an  API Object
#api = NVPApi()
api = NVPApi(debug=True)
#api = NVPApi(debug=True, verbose=True)

#print "Available Functions of the API"
# print dir(api)
print "\n"

# See an existing "Hypervisor Node"
print "Does Transport Node Exists?"
print api.tnode_exists("sclr045")
print "\n"

# Check for existing Transport Zones
print "Existing Transport Zones"
print api.get_transport_zones()
print "\n"

# Check for existing Transport Zone
print "Does the transport zone exist?"
print api.check_transport_exists("TZ")
print "\n"

# Check Control Cluster Nodes
print "Control Cluster Nodes"
nodes = api.get_control_cluster()
for node in nodes:
  print "\n"
  print node['display_name']
  for role in node['roles']:
     print "%s" % role['role']
     print "%s\n" % role['listen_addr']
print "\n"

# Check stats for interfaces on transport node
print "Get interface Statistics"
stats = api.get_interface_statistics(
   "80d9cb27-432c-43dc-9a6b-15d4c45005ee",
   "breth2+")
print "Interface %s" % ("breth2")
for stat, val in stats.iteritems():
   print "%s -- %s" % (stat, val)
print "\n"


