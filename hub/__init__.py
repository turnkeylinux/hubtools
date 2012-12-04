# 
# Copyright (c) 2011 Alon Swartz <alon@turnkeylinux.org>
# Copyright (c) 2012 Liraz Siri <liraz@turnkeylinux.org>
# 
# This file is part of HubTools.
# 
# HubTools is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
# 
from utils import API, HubAPIError
from appliances import Appliances
from servers import Servers
from backups import Backups

import time

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

class Spawner:
    """A high-level synchronous instance spawner that wraps around the Hub class"""

    WAIT_STATUS_FIRST = 15
    WAIT_STATUS = 10
    WAIT_RETRY = 5

    RETRIES = 2

    PENDING_TIMEOUT = 300

    class Error(Exception):
        pass

    class Stopped(Error):
        pass

    def __init__(self, apikey, wait_status_first=WAIT_STATUS_FIRST, wait_status=WAIT_STATUS, wait_retry=WAIT_RETRY, retries=RETRIES):

        self.apikey = apikey
        self.wait_status_first = wait_status_first
        self.wait_status = wait_status
        self.wait_retry = wait_retry
        self.retries = retries

    def _retry(self, callable, *args, **kwargs):
        for i in range(self.retries + 1):
            try:
                return callable(*args, **kwargs)
            except HubAPIError, e:
                if e.name == 'HubAccount.InvalidApiKey':
                    raise self.Error(e)

                if e.name == 'BackupRecord.NotFound':
                    raise self.Error(e)

                time.sleep(self.wait_retry)

        raise self.Error(e)

    def launch(self, name, howmany, logfh=None, callback=None, **kwargs):
        """launch <howmany> workers, wait until booted and yield (ipaddress, instanceid) tuples
        Invoke callback every frequently. If callback returns False, we terminate launching.
        """

        retry = self._retry
        hub = Hub(self.apikey)

        pending_ids = set()
        yielded_ids = set()

        time_start = time.time()
        wait_status = self.wait_status_first

        def get_pending_servers():
            if not pending_ids:
                return []

            return [ server 
                     for server in retry(hub.servers.get, refresh_cache=True)
                     if server.instanceid in (pending_ids - yielded_ids) ]
        
        def log(s):
            if logfh:
                logfh.write(s + "\n")

        stopped = None
        while True:

            if callback and not stopped:
                if callback() is False:
                    stopped = time.time()
                    log("launch stopped, destroying pending instances...")

            if stopped:
                servers = [ server for server in get_pending_servers() ]

                for server in servers:
                    if server.status == 'running':
                        retry(server.destroy, auto_unregister=True)
                        pending_ids.remove(server.instanceid)
                        log("destroyed instance %s" % server.instanceid)

                    if server.status == 'pending' and \
                       (time.time() - stopped > self.PENDING_TIMEOUT):
                        raise self.Error("stuck pending instance")

                if pending_ids:
                    time.sleep(self.wait_status)
                else:
                    raise self.Stopped

                continue

            if len(pending_ids) < howmany:
                server = retry(hub.servers.launch, name, **kwargs)
                pending_ids.add(server.instanceid)
                log("booting instance %s..." % server.instanceid)

            if (time.time() - time_start) >= wait_status:
                for server in get_pending_servers():
                    if server.status != 'running' or server.boot_status != 'booted':
                        continue

                    yielded_ids.add(server.instanceid)
                    yield (server.ipaddress, server.instanceid)

                if len(yielded_ids) == howmany:
                    break

                wait_status = self.wait_status
                time_start = time.time()

            time.sleep(0.2)

    def destroy(self, *addresses):
        """destroy addresses. An address can be an IP or an instance-id.
        Return a list of destroyed (ipaddress, instanceid) tuples"""
        if not addresses:
            return

        hub = Hub(self.apikey)
        retry = self._retry

        destroyable = [ server
                        for server in retry(hub.servers.get, refresh_cache=True)
                        if (server.ipaddress in addresses) or (server.instanceid in addresses) ]

        for server in destroyable:
            retry(server.destroy, auto_unregister=True)

        return [ (server.ipaddress, server.instanceid) for server in destroyable ]
