#!/usr/bin/python
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
"""
Destroy a cloud server

Arguments:

    instance_id           Instance ID of server to destroy

Options:

    --disable-unregister  Keep server configuration to re-launched later via Hub

Environment variables:

    HUB_APIKEY            Displayed in your Hub account's user profile
"""
import os
import sys
import getopt

from hub import Hub
from hub.utils import HubAPIError
from hub.formatter import fmt_server_header, fmt_server

def fatal(e):
    print >> sys.stderr, "error: " + str(e)
    sys.exit(1)

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Syntax: %s <instance_id> [opts]" % (sys.argv[0])
    print >> sys.stderr, __doc__

    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help", "disable-unregister"])
    except getopt.GetoptError, e:
        usage(e)

    auto_unregister = True
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        if opt == "--disable-unregister":
            auto_unregister = False

    if len(args) != 1:
        usage("incorrect number of arguments")
    instance_id = args[0]

    apikey = os.getenv('HUB_APIKEY', None)
    if not apikey:
        fatal("HUB_APIKEY not specified in environment")

    hub = Hub(apikey)

    try:
        server = hub.servers.get(instance_id)[0]
        server.destroy(auto_unregister=auto_unregister)
    except HubAPIError, e:
        fatal(e.description)

    print fmt_server_header()
    print fmt_server(server)

if __name__ == "__main__":
    main()

