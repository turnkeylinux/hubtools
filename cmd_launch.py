#!/usr/bin/python
"""
Launch a new cloud server

Arguments:
    appliance       Appliance name to launch (e.g. core)
    OR
    backup_id       Restore backup to a new cloud server (e.g. 2)

Options:
    --region        Region for instance launch (default: us-east-1)
    --type          Instance size (default: m1.small)
    --root-pass     Root password to set (default: random)
    --label         Optional server descriptive label

    --db-pass       Database password
    --app-pass      Admin password for application
    --app-email     Admin email address for application
    --app-domain    Domain for application

Environment variables:
    HUB_APIKEY      Displayed in your Hub account's user profile.
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
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", 
            ["help", "region=", "type=", "label=", "root-pass=", "db-pass=",
             "app-pass=", "app-email=", "app-domain="])
    except getopt.GetoptError, e:
        usage(e)

    kwargs = {
        'region': "us-east-1",
        'type': "m1.small",
        'label': "",
        'root_pass': "",
        'db_pass': "",
        'app_pass': "",
        'app_email': "",
        'app_domain': "",
    }
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

        for kwarg in kwargs.keys():
            if opt == '--' + kwarg.replace('_', '-'):
                kwargs[kwarg] = val
                break

    if len(args) != 1:
        usage("incorrect number of arguments")

    apikey = os.getenv('HUB_APIKEY', None)
    if not apikey:
        fatal("HUB_APIKEY not specified in environment")

    hub = Hub(apikey)

    try:
        kwargs['backup_id'] = int(args[0])
        record = hub.backups.get(kwargs['backup_id'])[0]
        m = re.match(r'turnkey-(.*?)-(\d.*|beta.*)', record.turnkey_version)
        appliance_name = m.groups()[0]
    except ValueError:
        appliance_name = args[0]
    except HubAPIError, e:
        fatal(e.description)

    try:
        server = hub.servers.launch(appliance_name, **kwargs)
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

