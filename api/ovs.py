#!/usr/bin/python
"""
ovs.py

Provides basic ovs initialization calls for nodes
that need to be setup as a transport node for
the NVP Control Cluster.

"""

import sys
import os
import re
import commands
import shutil
import time
import subprocess
from OpenSSL import crypto
from M2Crypto import ASN1
import datetime
import time
from common.util.util import *
 

def create_ovs_certs():
  execute(("rm -f /etc/openvswitch/vswitchd.cacert"))
  execute(("mkdir -p /etc/openvswitch"))
  if os.chdir("/etc/openvswitch") == 1:
    print "Unable to cd to directory %s" % key_path
    exit(1)
  execute(("ovs-pki init --force"))
  execute(("ovs-pki req+sign ovsclient controller --force"))
  execute(("ovs-vsctl -- --bootstrap set-ssl /etc/openvswitch/ovsclient-privkey.pem \
           /etc/openvswitch/ovsclient-cert.pem /etc/openvswitch/vswitchd.cacert"))

def connect_to_manager(ip):
  execute(("ovs-vsctl set-manager ssl:%s" % ip))
  execute(("ovs-vsctl br-set-external-id br-int bridge-id br-int"))

def install_bridges(interface):
  execute(("ovs-vsctl -- --may-exist add-br br-int"))
  cmd = "ovs-vsctl -- --may-exist add-br br-%s" % interface
  execute(cmd)
  cmd = "ovs-vsctl -- --may-exist  add-port br-%s %s" % (interface,interface)
  execute(cmd)

def get_cert_pem(text_cert):
  cert = crypto.load_certificate(crypto.FILETYPE_PEM, text_cert)
  pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
  return pem_cert

def ovs_init(ip, interface):
  create_ovs_certs()

  cmd = "cat /etc/openvswitch/ovsclient-cert.pem"
  status, text_cert = commands.getstatusoutput(cmd)

  if status != 0:
    print "/etc/openvswitch/ovsclient-cert.pem does not exist!"
    exit(1)

  cert = get_cert_pem(text_cert)

  connect_to_manager(ip)
  install_bridges(interface)

  return cert
