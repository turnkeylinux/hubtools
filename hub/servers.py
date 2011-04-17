from utils import AttrDict

class Server(AttrDict):
    def __repr__(self):
        return "<Server: %s (%s, %s)>" % (self.name, self.instanceid, self.status)

    def __init__(self, hubobj, response):
        self.hubobj = hubobj
        self._parse_response(response)

    def _parse_response(self, response):
        self.raw = response
        self.instanceid = response['instanceid']
        self.type = response['type']
        self.region = response['region']
        self.ipaddress = response['ipaddress']
        self.status = response['status']
        self.boot_status = response['server']['boot_status']
        self.name = response['server']['name']
        self.label = response['server']['description']

    def update(self):
        r = self.hubobj.api('GET', 'amazon/instance/%s/' % self.instanceid)
        self._parse_response(r)

    def reboot(self):
        r = self.hubobj.api('PUT', 'amazon/instance/%s/reboot/' % self.instanceid)
        self._parse_response(r)

    def terminate(self):
        r = self.hubobj.api('PUT', 'amazon/instance/%s/terminate/' % self.instanceid)
        self._parse_response(r)

    def unregister(self):
        self.hubobj.api('DELETE', 'amazon/instance/%s/unregister/' % self.instanceid)
  
class Servers(object):
    def __init__(self, hubobj):
        self.hubobj = hubobj

    def get(self, instanceid):
        r = self.hubobj.api('GET', 'amazon/instance/%s/' % instanceid)
        return Server(self.hubobj, r)

    def list(self):
        r = self.hubobj.api('GET', 'amazon/instances/')
        return map(lambda server: Server(self.hubobj, server), r)

