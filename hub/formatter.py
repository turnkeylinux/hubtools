def fmt_bool(bool):
    return "Yes" if bool else "No"

def fmt_size(bytes):
    if bytes < (10 * 1024):
        return "0.01"
    if bytes > (1024 * 1024 * 1000 * 99.99):
        return "%d" % (bytes / (1024 * 1024))
    else:
        return "%-.2f" % (bytes / (1024 * 1024.0))

def fmt_status(status, boot_status):
    if status == "running" and not boot_status == "booted":
        return boot_status
    return status

def fmt_backup_header():
    return "# ID  SKPP  Created     Updated     Size (MB)  Label"

def fmt_backup(backup):
    return "%4s  %-3s   %s  %-10s  %-8s   %s" % \
        (backup.backup_id,
         fmt_bool(backup.skpp),
         backup.created.strftime("%Y-%m-%d"),
         backup.updated.strftime("%Y-%m-%d") if backup.updated else "-",
         fmt_size(backup.size),
         backup.label)

def fmt_server_header():
    return "# Status    ID         IP Address      Region          Label"

def fmt_server(server):
    return "%-10s  %-9s  %-14s  %-14s  %s" % \
        (fmt_status(server.status, server.boot_status),
         "i-1234%s" % server.instanceid,
         server.ipaddress if server.ipaddress else "-",
         server.region,
         server.label)
