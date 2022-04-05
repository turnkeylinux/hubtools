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
from .attrdict import AttrDict

class Appliance(AttrDict):
    def __repr__(self):
        return "<Appliance: %s>" % self.name

    def __init__(self, response):
        self.raw = response
        self.name = response['name']
        self.version = response['version']
        self.description = response['description']
        self.preseeds = response['preseeds']

        AttrDict.__init__(self)

class Appliances(object):
    def __init__(self, api):
        self.api = api

    def get(self, name=None):
        if name:
            r = self.api('GET', 'amazon/appliance/%s/' % name)
        else:
            r = self.api('GET', 'amazon/appliances/')

        return [ Appliance(appliance) for appliance in r ]
