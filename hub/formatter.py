def fmt_bool(bool):
    return "Yes" if bool else "No"

def fmt_size(bytes):
    if bytes < (10 * 1024):
        return "0.01"
    if bytes > (1024 * 1024 * 1000 * 99.99):
        return "%d" % (bytes / (1024 * 1024))
    else:
        return "%-.2f" % (bytes / (1024 * 1024.0))

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
