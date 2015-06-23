#!/usr/bin/env python3
import yaml
from os.path import expanduser
import os

config = {
    'identity': '~/.ssh/id_rsa'
}

if os.path.isfile("config.yml"):
    with open("config.yml") as settings:
        config.update(yaml.load(settings))

identity_file = config['identity']

with open(expanduser("~/.ssh/config.pre")) as pre:
    connections = pre.read()

connections += "\n\n"

with open(expanduser("~/.ssh/hostinfo.yml")) as hostinfofile:
    hostinfo = yaml.load(hostinfofile)
    for jumphost in hostinfo:
        connections += "Host {}\n".format(jumphost)
        if 'user' in hostinfo[jumphost]:
            connections += "\tUser {}\n".format(hostinfo[jumphost]['user'])
        else:
            connections += "\tUser root\n"
        connections += "\tHostname {}\n".format(hostinfo[jumphost]['host'])
        connections += "\tIdentityFile {}\n".format(identity_file)
        connections += "\n"

        prefix = hostinfo[jumphost]['prefix']

        for subhost in hostinfo[jumphost]['subhosts']:
            name = hostinfo[jumphost]['subhosts'][subhost]
            connections += "Host {}.{}\n".format(jumphost, name)
            connections += "\tUser root\n"
            connections += "\tHostname {}{}\n".format(prefix, subhost)
            connections += "\tProxyCommand ssh {} netcat -w 120 %h %p\n".format(jumphost)
            connections += "\tIdentityFile {}\n".format(identity_file)
            connections += "\n"

with open(expanduser("~/.ssh/config"), "w") as config_file:
    config_file.write(connections)
