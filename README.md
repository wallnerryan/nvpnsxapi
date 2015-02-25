##Nicira NVP/NSX Python API and Infrstructure Automation
=========================

##About
=========================

There are two main uses for this python library:

(1) **Manage NVP/NSX Infrastructure**

Managing, automating, and orchestrating the setup of NVP/NSX components 
eleminates repetative CLI commands. Spin up and down environments on the fly,
and or manage upgrading new components when you want to upgrade.

The Library allows you to remotely setup Hypervisor Nodes, Gateway
Nodes, Service Nodes etc. (Examples Below)

(2) **Python bindings to NVP/NSX REST API**

Having python bindings was the first motivation. 
	A) because we developed and were familiar with Python 
	B) We have been working with OpenStack and it just made sense.

With the library you can list networking, attach ports, query nodes etc.
*(Examples are given in the test/example_api_usage.py)

*Desclaimer, this is not a full-blown, fully featured API binding. There are
missing binding for NVP API versions as well as NSX versions. If the API call does
not exist, I welcome any patches.

* Note, all api calls have been tested on NVP 3.0-3.2
* Note, only partially tested on NSX 4.1.X

##Authors
=========================

@Ryan Wallner (Ryan.Wallner@emc.com)

##Installation API
========================

```
apt-get install python-simplejson \
                python-m2crypto \
                python-pexpect

git clone https://github.com/wallnerryan/nvpnsxapi
```


##Example Usage API
=========================

Before you use the API, we need some simple
configuration.
(This will all happen automatically when we
make this pip insatllable.)

```
cp ../nvpnsxapi/etc/nvp.conf /etc/nvp.conf
(edit the fields inside here.)

Default are

[nvp-controller]
user: admin
password: admin
ip: <X.X.X.X>
port: 443
zone: 'MyTransportZone'
config-file: /etc/nvp/configs/nvp-config.json
snapshot-location: /etc/nvp/snapshots
```

```python
from api.nvp_api import NVPApi

api = NVPApi(debug=True)

transport_zones = api.get_transport_zones()

exists = api.tnode_exists("My-ESX-Node")

print "Transport Zones Are: %s" % transport_zones
print "Doest MyTransportNode exists? %s" % exists

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
```

##Example Automation
=========================

For automation, openvswitch, nvp/nsx packages must be installed on
the target node. Automation has been testd ONLY for Hypervisor, Service,
and Gateway Nodes.

NSX/NVP packges must be installed on target node, here is an 
example for a NVP hypervisor

To use this feature you need to update the JSON
configuration file that describes your environment.

There is not CLI/Automated Tool to fill this out,
use your favorite JSON editor :)

Example Node "Node1"
```
cp ../nvpnsxapi/automation/configs/nvp-config-example.json /etc/nvp/configs/nvp-config.json
vi /etc/nvp/configs/nvp-config.json

You will the following top level objects

config
    transport-zones
    nvp
    transport-types
    transport-nodes
    trasnport-ip-prefixes
    nat
    routers
    gateway-services

In update the following objects

(Transport Nodes)
transport-zones":{
      "zone":[
        {
          "type":"<STT/VXLAN>",
          "name":"<YourTransportZoneName>"
        }
      ]

(NVP Config)
"nvp":{
      "ip":"<CONTROLLER_IP>",
      "pass":"<Password>",
      "port":<443 | 80>,
      "user":"<UserName>"
    }


(Add a "Hypervisor Node" description. Replace what is in the < >)
"transport-nodes":{
      "node":[
        {
          "type":"COMPUTE",
          "remote": <true | false>,
          "management-address":"<X.X.X.X>",
          "integration-bridge":"<br-int>",
          "data-network-interface":"<eth1 | eth2 ...>",
          "connectors":[
            {
              "ip_address":"<X.X.X.X>",
              "type":"<STTConnector?>",
              "name":"<TransportZoneConnectorName>"
            }
          ],
          "name":"<myServer>"
        },

# There are other objects you can change, feel free to, this will
# get what is in the README demo working.
```

```
# Initialize OVS on the Hypervisor Node
sudo dpkg --purge openvswitch-pki 
sudo dpkg -i openvswitch-datapath-dkms_1.11.0*.deb 
sudo dpkg -i openvswitch-common_1.11.0*.deb openvswitch-switch_1.11.0*.deb 
sudo dpkg -i nicira-ovs-hypervisor-node_1.11.0*.deb

(If Node1 is remote, it will prompt for Username/Password)
python -m automation.transportnode create <NodeName>
```
You should then be able to go to NVP/NSX Web GUI and view the new transport node.
GUI for NVP 3.2 Tested here can be viewed at https://<Cluster-IP-Address>/accounts/login/

##Future (TODO)
========================

As stated earlier, this is not a complete solution, nor should it be used as one.
There is no guarantee for the use of this product and should solely be used to
help setup and test in a lab environment.

* API Bindings need to be added for missing endpoints
* Tests / Simple Testing Framework that mocks networks needs to be developed
* Automated / Packaged build and install needs to be included.
* NSX Support (api endpoints, xml support, etc)

## Contribution
Create a fork of the project into your own reposity. Make all your necessary changes 
in a seperate branch and create a pull request with a description on what was added 
or removed and details explaining the changes in lines of code. If approved, 
project owners will merge it.

Licensing
---------
View LICENSE in src.

Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except 
in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on 
an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the 
specific language governing permissions and limitations under the License.


Support
-------
Please file bugs and issues at the Github issues page. The code and documentation are 
released with no warranties or SLAs and are intended to be supported through a community driven process.

For more general questions, please email Ryan.Wallner@emc.com

Other Information
------

Please see the below links for more inspiraton

[Using Curl to Interact with a RESTful API](http://blog.scottlowe.org/2014/02/19/using-curl-to-interact-with-a-restful-api/)

[NSX API Guide](https://pubs.vmware.com/NSX-6/topic/com.vmware.ICbase/PDF/nsx_604_api.pdf)
