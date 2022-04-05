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
Launch a new cloud server

Arguments:

    appliance          Appliance name to launch (e.g. core)

Options:

    --region=          Region for instance launch (default: us-east-1)
    --size=            Instance size (default: m1.small)
    --label=           Optional server descriptive label

    --root-pass=       Root password to set (default: random)
    --db-pass=         Database password
    --app-pass=        Admin password for application
    --app-email=       Admin email address for application
    --app-domain=      Domain for application

    --backup-id=       TurnKey Backup ID to restore on launch
    --fqdn=            Fully qualified domain name to associate
                       e.g., www.tklapp.com. | www.example.com.

    --skip-secalerts   Skip firstboot security updates
    --skip-secupdates  Skip security alerts and notifications setup

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

    print("Syntax: %s <appliance> [opts]" % (sys.argv[0]), file=sys.stderr)
    print(__doc__, file=sys.stderr)

    sys.exit(1)

def main():
    kwargs = {
        'region': "us-east-1",
        'size': "m1.small",
        'label': "",
        'root_pass': "",
        'db_pass': "",
        'app_pass': "",
        'app_email': "",
        'app_domain': "",
        'fqdn': "",
        'backup_id': "",
        'sec_alerts': "FORCE",
        'sec_updates': "FORCE",
    }
    try:
        s_opts = "h"
        l_opts = [key.replace("_", "-") + "=" for key in kwargs ]
        l_opts.extend(["help", "skip-secalerts", "skip-secupdates"])
        opts, args = getopt.gnu_getopt(sys.argv[1:], s_opts, l_opts)
    except getopt.GetoptError as e:
        usage(e)

    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        if opt == '--skip-secalerts':
            kwargs['sec_alerts'] = 'SKIP'
            continue

        if opt == '--skip-secupdates':
            kwargs['sec_updates'] = 'SKIP'
            continue

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
    except hub.Error as e:
        if e.name == "Request.MissingArgument":
            arg = e.description.split()[-1]
            fatal("Required argument: --" + arg.replace('_', '-'))
        else:
            fatal(e.description)

    print(fmt_server_header())
    print(fmt_server(server))

if __name__ == "__main__":
    main()

