from utils import AttrDict

from datetime import datetime

class BackupRecord(AttrDict):
    def __repr__(self):
        return "<BackupRecord: %s>" % self.backup_id

    def __init__(self, hubobj, response):
        self.hubobj = hubobj
        self._parse_response(response)

    @staticmethod
    def _parse_datetime(s):
        if not s:
            return None

        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    def _parse_response(self, response):
        self.raw = response
        self.key = response['key']
        self.address = response['address']
        self.backup_id = response['backup_id']
        self.server_id = response['server_id']
        self.turnkey_version = response['turnkey_version']

        self.created = self._parse_datetime(response['date_created'])
        self.updated = self._parse_datetime(response['date_updated'])

        self.size = int(response['size']) # in MBs
        self.label = response['description']

class Backups(object):
    def __init__(self, hubobj):
        self.hubobj = hubobj

    def get(self, backup_id=None):
        if backup_id:
            r = self.hubobj.api('GET', 'backup/record/%s/' % backup_id)
            return [ BackupRecord(self.hubobj, r) ]
        else:
            r = self.hubobj.api('GET', 'backup/records/')
            return map(lambda backup: BackupRecord(self.hubobj, backup), r)

