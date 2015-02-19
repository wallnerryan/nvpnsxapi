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

def create_ovs_certs(s):
    s.sudo_execute(("rm -f /etc/openvswitch/vswitchd.cacert"))
    s.sudo_execute(("mkdir -p /etc/openvswitch"))
    s.sudo_execute(("ovs-pki init --force"))
    s.sudo_execute(("ovs-pki req+sign ovsclient controller --force"))
    s.sudo_execute(("ovs-vsctl -- --bootstrap set-ssl /etc/openvswitch/ovsclient-privkey.pem" \
           " /etc/openvswitch/ovsclient-cert.pem /etc/openvswitch/vswitchd.cacert"))

def connect_to_manager(s,ip):
    s.sudo_execute(("ovs-vsctl set-manager ssl:%s" % ip))
    s.sudo_execute(("ovs-vsctl br-set-external-id br-int bridge-id br-int"))

def install_bridges(s,interface):
    s.sudo_execute(("ovs-vsctl -- --may-exist add-br br-int"))
    cmd = "ovs-vsctl -- --may-exist add-br br-%s" % interface
    s.sudo_execute(cmd)
    cmd = "ovs-vsctl -- --may-exist  add-port br-%s %s" % (interface,interface)
    s.sudo_execute(cmd)

def get_cert_pem(text_cert):
  cert = crypto.load_certificate(crypto.FILETYPE_PEM, text_cert)
  pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
  return pem_cert

# Remote Ovs Init, does the same thing, but we must pass an
# SSH object to it, using "nvp.common.remote_ssh"
def remote_ovs_init(s,ip, interface):
  create_ovs_certs(s)

  cmd = "cat /etc/openvswitch/ovsclient-cert.pem"
  (status, data) = s.sudo_execute(cmd)
  #status = status.recv_exit_status() #NEED STATUS
  print "printing status"
  print status
  print data
  
  if status != 0:
    print "/etc/openvswitch/ovsclient-cert.pem does not exist!"
    exit(1)
  
  cert = get_cert_pem(data)

  connect_to_manager(s,ip)
  install_bridges(s,interface)

  return cert
