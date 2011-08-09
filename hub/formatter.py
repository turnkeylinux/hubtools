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
import string

# custom formatting
class Formatter:
    def __init__(self, format):
        tpl = format.replace('$', '$$')
        tpl = tpl.replace('\\n', '\n')
        tpl = tpl.replace('\\t', '\t')
        tpl = tpl.replace('%%', '__PERCENT__')
        tpl = tpl.replace('%', '$')
        tpl = tpl.replace('__PERCENT__', '%')

        self.tpl = string.Template(tpl)

    def __call__(self, obj):
        return self.tpl.substitute(**obj)

# helper formatting
def _fmt_bool(bool):
    return "Yes" if bool else "No"

def _fmt_size(bytes):
    if bytes < (10 * 1024):
        return "0.01"
    if bytes > (1024 * 1024 * 1000 * 99.99):
        return "%d" % (bytes / (1024 * 1024))
    else:
        return "%-.2f" % (bytes / (1024 * 1024.0))

def _fmt_status(status, boot_status):
    if status == "running" and not boot_status == "booted":
        return boot_status
    return status

# backup formatters
def fmt_backup_header():
    return "# ID  SKPP  Created     Updated     Size (MB)  Label"

def fmt_backup(backup):
    return "%4s  %-3s   %s  %-10s  %-8s   %s" % \
        (backup.backup_id,
         _fmt_bool(backup.skpp),
         backup.created.strftime("%Y-%m-%d"),
         backup.updated.strftime("%Y-%m-%d") if backup.updated else "-",
         _fmt_size(backup.size),
         backup.label)

# server formatters
def fmt_server_header():
    return "# Status          ID         IP Address       Region          Label"

def fmt_server(server):
    return "  %-14s  %-9s  %-15s  %-14s  %s" % \
        (_fmt_status(server.status, server.boot_status),
         server.instanceid,
         server.ipaddress if server.ipaddress else "-",
         server.region,
         server.label)

# appliance formatters
def fmt_appliance_header():
    return "# Name               Ver.  Preseeds"

def fmt_appliance(appliance):
    return "  %-17s  %s  %s" % \
        (appliance.name,
         appliance.version.split('-')[0],
         "root_pass %s" % " ".join(appliance.preseeds))

