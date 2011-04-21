#!/usr/bin/python
"""
List appliances

Environment variables:
    HUB_APIKEY      Displayed in your Hub account's user profile.
"""
import os
import sys
import getopt

from hub import Hub
from hub.formatter import fmt_appliance_header, fmt_appliance

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
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError, e:
        usage(e)

    refresh = False
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()

    apikey = os.getenv('HUB_APIKEY', None)
    if not apikey:
        fatal("HUB_APIKEY not specified in environment")

    hub = Hub(apikey)

    appliances = hub.appliances.get()
    appliances = sorted(appliances, key=lambda appliance: appliance.name)

    print fmt_appliance_header()
    for appliance in appliances:
        print fmt_appliance(appliance)

if __name__ == "__main__":
    main()

