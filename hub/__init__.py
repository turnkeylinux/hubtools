from utils import API
from appliances import Appliances
from servers import Servers
from backups import Backups

class Hub(object):
    """Top-level object to access the TurnKey Hub API"""
    API_URL = 'https://hub.turnkeylinux.org/api/'
    API_HEADERS = {'Accept': 'application/json'}

    def __init__(self, apikey=None):
        self.apikey = apikey
        self.appliances = Appliances(self)
        self.servers = Servers(self)
        self.backups = Backups(self)

    def api(self, method, uri, attrs={}):
        headers = self.API_HEADERS.copy()
        if self.apikey:
            headers['apikey'] = self.apikey
        return API.request(method, self.API_URL + uri, attrs, headers)

