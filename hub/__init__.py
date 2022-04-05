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
from .appliances import Appliances
from .servers import Servers
from .backups import Backups

import time

from pycurl_wrapper import API

class Hub(object):
    Error = API.Error

    """Top-level object to access the TurnKey Hub API"""
    API_URL = 'https://hub.turnkeylinux.org/api/'

    def __init__(self, apikey=None, timeout=None, verbose=False):
        headers = {}
        if apikey:
            headers['apikey'] = apikey

        _api = API(timeout=timeout, verbose=verbose)
        def api(method, uri, attrs={}):
            return _api.request(method, self.API_URL + uri, attrs, headers)

        self.appliances = Appliances(api)
        self.servers = Servers(api)
        self.backups = Backups(api)

class Spawner:
    """A high-level synchronous instance spawner that wraps around the Hub class"""

    WAIT_STATUS_FIRST = 25
    WAIT_STATUS = 10
    WAIT_RETRY = 5

    API_RETRIES = 3
    API_TIMEOUT = 30

    PENDING_TIMEOUT = 300

    class Error(Exception):
        pass

    class Stopped(Error):
        pass

    def __init__(self, apikey, wait_status_first=WAIT_STATUS_FIRST, wait_status=WAIT_STATUS, wait_retry=WAIT_RETRY, api_retries=API_RETRIES, api_timeout=API_TIMEOUT):

        self.hub = Hub(apikey, timeout=api_timeout)

        self.wait_status_first = wait_status_first
        self.wait_status = wait_status
        self.wait_retry = wait_retry

        self.api_retries = api_retries

    def _retry(self, callable, *args, **kwargs):
        for i in range(self.api_retries + 1):
            try:
                return callable(*args, **kwargs)
            except self.hub.Error as e:
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

        pending_ids = set()
        yielded_ids = set()

        time_start = time.time()
        wait_status = self.wait_status_first

        def get_pending_servers():
            if not pending_ids:
                return []

            return [ server
                     for server in retry(self.hub.servers.get, refresh_cache=True)
                     if server.instanceid in (pending_ids - yielded_ids) ]

        def log(s):
            if logfh:
                logfh.write(s + "\n")

        stopped = None

        launch_failure = None
        launch_failure_pending = None

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

                    elif server.status in ('stopped', 'terminated'):
                        pending_ids.remove(server.instanceid)

                    elif server.status == 'pending' and \
                       (time.time() - stopped > self.PENDING_TIMEOUT):
                        raise self.Error("stuck pending instance")

                if not pending_ids or not servers:
                    raise self.Stopped
                else:
                    time.sleep(self.wait_status)

                continue

            if len(pending_ids) < howmany and not launch_failure:
                try:
                    server = retry(self.hub.servers.launch, name, **kwargs)
                    pending_ids.add(server.instanceid)
                    log("booting instance %s ..." % server.instanceid)
                except Exception as e:

                    if pending_ids:
                        log("failed to launch instance, waiting for %d pending instances" % len(pending_ids))
                    else:
                        log("failed to launch instance")

                    launch_failure = e
                    launch_failure_pending = len(pending_ids)

            if launch_failure and len(yielded_ids) == launch_failure_pending:
                raise launch_failure

            if (time.time() - time_start) >= wait_status:
                pending_servers = get_pending_servers()

                missing_ids = pending_ids - yielded_ids - set([ server.instanceid for server in pending_servers ])
                for missing_id in missing_ids:
                    pending_ids.remove(missing_id)

                for server in pending_servers:
                    if server.status in ('stopped', 'terminated'):
                        pending_ids.remove(server.instanceid)
                        continue

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

        retry = self._retry

        destroyable = [ server
                        for server in retry(self.hub.servers.get, refresh_cache=True)
                        if (server.ipaddress in addresses) or (server.instanceid in addresses) ]

        for server in destroyable:
            retry(server.destroy, auto_unregister=True)

        return [ (server.ipaddress, server.instanceid) for server in destroyable ]
