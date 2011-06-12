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
List servers

Options:

    -r --refresh    Force refresh of Hubs Amazon EC2 cache

By default uses a built-in format, unless a user-specified format is specified.
Format variables:

    %instanceid         Instance ID
    %size               Instance size
    %type               Instance type
    %region             Instance region
    %label              Descriptive label
    %name               Appliance code name
    %ipaddress          Associated IP address
    %status             Amazon EC2 reported status
    %boot_status        Hub status (sec-updates, tklbam-restore, etc.)

Examples:

    hub-list-servers
    hub-list-servers "instanceid=%instanceid status=%status ipaddress=%ipaddress"

Environment variables:

    HUB_APIKEY          Displayed in your Hub account's user profile
"""
import os
import sys
import getopt

from hub import Hub
from hub.formatter import Formatter, fmt_server_header, fmt_server

def fatal(e):
    print >> sys.stderr, "error: " + str(e)
    sys.exit(1)

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Syntax: %s" % (sys.argv[0])
    print >> sys.stderr, __doc__

    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hr", ["help", "refresh"])
    except getopt.GetoptError, e:
        usage(e)

    refresh = False
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-r', '--refresh'):
            refresh = True

    if args:
        if len(args) != 1:
            usage("incorrect number of arguments")

        format = args[0]
    else:
        format = None

    apikey = os.getenv('HUB_APIKEY', None)
    if not apikey:
        fatal("HUB_APIKEY not specified in environment")

    hub = Hub(apikey)
    servers = hub.servers.get(refresh_cache=refresh)
    if servers:
        servers = sorted(servers, key=lambda server: server.status)
        if format:
            format = Formatter(format)
            for server in servers:
                print format(server)
        else:
            print fmt_server_header()
            for server in servers:
                print fmt_server(server)

if __name__ == "__main__":
    main()

