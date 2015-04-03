Nicira NVP/NSX Python API and Infrstructure Automation
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
(Examples are given in the test/example_api_usage.py)

Desclaimer, this is not a full-blown, fully featured API binding. There are
missing binding for NVP API versions as well as NSX versions. If the API call does
not exist, I welcome any patches.

* Note, all api calls have been tested on NVP 3.0-3.2
* Note, only partially tested on NSX 4.1.X


What's New?
===========
