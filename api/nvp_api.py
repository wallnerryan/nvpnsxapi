from nvp2 import NVPClient
from transport import Transport
from network_services import NetworkServices
from control_services import ControlServices
import logging

class NVPApi(Transport,
             NetworkServices,
             ControlServices):
    #Shared
    client = NVPClient()
    log = logging
    def __init__(self, debug=False, verbose=False):
        self.client.login()
        if verbose:
          self.log.basicConfig(level=self.log.INFO)
        if debug:
          self.log.basicConfig(level=self.log.DEBUG)
        Transport.__init__(self, self.client, self.log)
        NetworkServices.__init__(self, self.client, self.log)
        ControlServices.__init__(self, self.client, self.log)
