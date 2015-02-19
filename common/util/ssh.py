'''
Created on July 11th, 2013

@author: Layne
@edited: Ryan Wallner

'''

import logging

import paramiko, base64
import time

logger = logging.getLogger(__name__)

class ssh_client:
    client = None
    host = None
    username = None
    password = None
    
    def __init__(self, host, port, username, password):
        self.host = host
        self.username = username
        self.password = password
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logger.info('*** Connecting...')
        logger.info("Host: %s Username: %s Password: %s", host, username, password)
        self.client.connect(str(host), port, username, password) 
        
        
    def execute(self, cmd):
        _, stdout, stderr = self.client.exec_command(cmd)
        out = map(lambda line : line, stdout)
        err = map(lambda line : line, stderr)
        
        return out, err

    # @def sudo_execute
    # Uses provided password to make remote
    # "sudo" commands. User must be able to sudo
    # on remote host.
    def sudo_execute(self, cmd):
        print "Sending... %s" % cmd
        transport = self.client.get_transport()
        sess = transport.open_session()
        sess.get_pty()
        sess.exec_command("sudo " + cmd + "\n")
        status = None
        data = None
        while True:
            if sess.recv_ready():
                time.sleep(1)
                if sess.send_ready():
                  sess.send("%s\n" % self.password)
                  time.sleep(1)
                  data =  sess.recv(65536)
                  logger.info("Received: %s" % data)
                  status = sess.recv_exit_status()
                  logger.info("Exit status: %d" % status)
            if sess.exit_status_ready():
              #status = session1.recv_exit_status()
              break
        sess.close()
        return (status, data)
    
    def close(self):
        self.client.close