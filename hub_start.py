#!/usr/bin/env python
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
Start a stopped EBS backed cloud server

Arguments:

    instance_id     Instance ID of server to terminate

Environment variables:

    HUB_APIKEY      Displayed in your Hub account's user profile
"""
import os
import sys
import getopt

from hub import Hub
from hub.formatter import fmt_server_header, fmt_server

def fatal(e):
    print("error: " + str(e), file=sys.stderr)
    sys.exit(1)

def usage(e=None):
    if e:
        print("error: " + str(e), file=sys.stderr)

    print("Syntax: %s <instance_id>" % (sys.argv[0]), file=sys.stderr)
    print(__doc__, file=sys.stderr)

    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError as e:
        usage(e)

    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

    if len(args) != 1:
        usage("incorrect number of arguments")
    instance_id = args[0]

    apikey = os.getenv('HUB_APIKEY', None)
    if not apikey:
        fatal("HUB_APIKEY not specified in environment")

    hub = Hub(apikey)

    try:
        server = hub.servers.get(instance_id)[0]
        server.start()
    except hub.Error as e:
        fatal(e.description)

    print(fmt_server_header())
    print(fmt_server(server))

if __name__ == "__main__":
    main()

