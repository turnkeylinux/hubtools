#!/usr/bin/python
"""
Terminate a cloud server

Arguments:
    instance_id     Instance ID of server to terminate

Environment variables:
    HUB_APIKEY      Displayed in your Hub account's user profile.
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

    print >> sys.stderr, "Syntax: %s <instance_id>" % (sys.argv[0])
    print >> sys.stderr, __doc__

    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError, e:
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
        server.terminate()
    except HubAPIError, e:
        fatal(e.description)

    print fmt_server_header()
    print fmt_server(server)

if __name__ == "__main__":
    main()

