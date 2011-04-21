# 
# Copyright (c) 2011 Alon Swartz <alon@turnkeylinux.org>
# 
# This file is part of HubTools.
# 
# HubTools is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
# 
import keypacket
from utils import AttrDict

from datetime import datetime

class BackupRecord(AttrDict):
    def __repr__(self):
        return "<BackupRecord: %s>" % self.backup_id

    def __init__(self, hubobj, response):
        self.hubobj = hubobj
        self._parse_response(response)

    @staticmethod
    def _key_has_passphrase(key):
        try:
            keypacket.parse(key, "")
            return False
        except keypacket.Error:
            return True

    @staticmethod
    def _parse_datetime(s):
        if not s:
            return None

        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    def _parse_response(self, response):
        self.raw = response
        self.address = response['address']
        self.backup_id = response['backup_id']
        self.server_id = response['server_id']
        self.turnkey_version = response['turnkey_version']
        self.skpp = self._key_has_passphrase(response['key'])

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

