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
Launch a new cloud server

Arguments:

    appliance       Appliance name to launch (e.g. core)
    OR
    backup_id       Restore backup to a new cloud server (e.g. 2)

Options:

    --region        Region for instance launch (default: us-east-1)
                    Regions:

                      us-east-1 (Virginia, USA)
                      us-west-1 (California, USA)
                      eu-west-1 (Ireland, Europe)
                      ap-southeast-1 (Singapore, Asia)

    --size          Instance size (default: m1.small)
                    Sizes:

                      t1.micro (1 CPU core, 613M RAM, no tmp storage)
                      m1.small (1 CPU core, 1.7G RAM, 160G tmp storage)
                      c1.medium (2 CPU cores, 1.7G RAM, 350G tmp storage)

    --type          Instance type <s3|ebs> (default: s3)
    --label         Optional server descriptive label

    --root-pass     Root password to set (default: random)
    --db-pass       Database password
    --app-pass      Admin password for application
    --app-email     Admin email address for application
    --app-domain    Domain for application

    --fqdn          Fully qualified domain name to associate
                    e.g., www.tklapp.com. | www.example.com.

Environment variables:

    HUB_APIKEY      Displayed in your Hub account's user profile
"""
import re
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

    print >> sys.stderr, "Syntax: %s <appliance|backup_id> [opts]" % (sys.argv[0])
    print >> sys.stderr, __doc__

    sys.exit(1)

def main():
    kwargs = {
        'region': "us-east-1",
        'size': "m1.small",
        'type': "s3",
        'label': "",
        'root_pass': "",
        'db_pass': "",
        'app_pass': "",
        'app_email': "",
        'app_domain': "",
        'fqdn': "",
    }
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", 
                                       ["help" ] + 
                                       [  key.replace("_", "-") + "=" for key in kwargs ])
    except getopt.GetoptError, e:
        usage(e)

    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        for kwarg in kwargs:
            if opt == '--' + kwarg.replace('_', '-'):
                kwargs[kwarg] = val
                break

    if len(args) != 1:
        usage("incorrect number of arguments")

    apikey = os.environ.get('HUB_APIKEY')
    if not apikey:
        fatal("HUB_APIKEY not specified in environment")

    name = args[0]
    hub = Hub(apikey)

    try:
        server = hub.servers.launch(name, **kwargs)
    except HubAPIError, e:
        if e.name == "Request.MissingArgument":
            arg = e.description.split()[-1]
            fatal("Required argument: --" + arg.replace('_', '-'))
        else:
            fatal(e.description)
        
    print fmt_server_header()
    print fmt_server(server)

if __name__ == "__main__":
    main()

