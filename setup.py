# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import re
import os.path
import commands

from distutils.core import setup

class ExecError(Exception):
    pass

def _getoutput(command):
    status, output = commands.getstatusoutput(command)
    if status != 0:
        raise ExecError()
    return output

def get_version():
    output = _getoutput("dpkg-parsechangelog")
    version = [ line.split(" ")[1]
                for line in output.split("\n")
                if line.startswith("Version:") ][0]
    return version

def parse_control(control):
    """parse control fields -> dict"""
    d = {}
    for line in control.split("\n"):
        if not line or line[0] == " ":
            continue
        line = line.strip()
        i = line.index(':')
        key = line[:i]
        val = line[i + 2:]
        d[key] = val

    return d

def parse_email(email):
    m = re.match(r'(.*)\s*<(.*)>', email.strip())
    if m:
        name, address = m.groups()
    else:
        name = ""
        address = email

    return name.strip(), address.strip()

def main():
    control_fields = parse_control(file("debian/control").read())
    maintainer = control_fields['Maintainer']
    maintainer_name, maintainer_email = parse_email(maintainer)

    setup(packages = ['hub'],
          # non-essential meta-data
          name=control_fields['Source'],
          version=get_version(),
          maintainer=maintainer_name,
          maintainer_email=maintainer_email,
          description=control_fields['Description'])

if __name__=="__main__":
    main()


