#!/usr/bin/python3

from distutils.core import setup

setup(
    name="hubtools",
    version="1.1",
    author="Jeremy Davis",
    author_email="jeremy@turnkeylinux.org",
    url="https://github.com/turnkeylinux/hubtools",
    packages=["hublib"],
    scripts=["hub_destroy.py",
             "hub_launch.py",
             "hub_list_appliances.py",
             "hub_list_backups.py",
             "hub_list_servers.py",
             "hub_start.py",
             "hub_stop.py"]
)
