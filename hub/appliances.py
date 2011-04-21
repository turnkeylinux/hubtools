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
from utils import AttrDict

class Appliance(AttrDict):
    def __repr__(self):
        return "<Appliance: %s>" % self.name

    def __init__(self, hubobj, response):
        self.hubobj = hubobj
        self._parse_response(response)

    def _parse_response(self, response):
        self.raw = response
        self.name = response['name']
        self.version = response['version']
        self.description = response['description']
        self.preseeds = response['preseeds']

class Appliances(object):
    def __init__(self, hubobj):
        self.hubobj = hubobj

    def get(self, name=None):
        if name:
            r = self.hubobj.api('GET', 'amazon/appliance/%s/' % name)
        else:
            r = self.hubobj.api('GET', 'amazon/appliances/')

        return map(lambda appliance: Appliance(self.hubobj, appliance), r)

