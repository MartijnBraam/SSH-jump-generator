#!/usr/bin/env python3
import yaml
from os.path import expanduser
import os
import sys
import subprocess
from tabulate import tabulate
from collections import OrderedDict

config = {
    'identity': '~/.ssh/id_rsa'
}

if os.path.isfile("config.yml"):
    with open("config.yml") as settings:
        config.update(yaml.load(settings))

report = {}


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    This function is from http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def fix_host(name):
    global config
    command = ['ssh-copy-id', '-i', config['identity'], name]
    return subprocess.call(command) == 0


def check_host(name, interactive=False):
    global report
    print("\tChecking {}...".format(name), end="", flush=True)
    command = ['ssh', '-oBatchMode=yes', name, 'echo test']
    if interactive:
        command.remove('-oBatchMode=yes')
    proc = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    stdout = stdout.decode('utf8')
    stderr = stderr.decode('utf8')
    if proc.returncode == 0:
        print("[OK]")
        if interactive:
            print("\t\tHost key fixed. Retrying non-interactive for identity check")
            report[name] = 'Password login only'
            check_host(name)
        else:
            report[name] = 'OK'
    else:
        if 'Host key verification failed' in stderr:
            print("[ERR]")
            print("\t\tHost key verification failed")
            print("\t\tRetrying in interactive mode")
            report[name] = 'Host key verification failed'
            check_host(name, interactive=True)
        elif 'Permission denied' in stderr:
            print("[ERR]")
            print("\t\tIdentity not installed on {}".format(name))
            report[name] = 'Password login only'
            if query_yes_no("\t\tDo you want to upload identity {} to {}?".format(config['identity'], name),
                            default="yes"):
                if fix_host(name):
                    report[name] = 'OK'
                else:
                    report[name] = 'Error installing key'
            else:
                print("\t\tNot installing identity")
        else:
            print("[ERR]")
            report[name] = 'Unknown error'


with open(expanduser("~/.ssh/hostinfo.yml")) as hostinfofile:
    hostinfo = yaml.load(hostinfofile)
    for jumphost in hostinfo:
        print("# Checking keys for jumphost {}".format(jumphost))
        check_host(jumphost)
        for subhost in hostinfo[jumphost]['subhosts']:
            name = hostinfo[jumphost]['subhosts'][subhost]
            check_host("{}.{}".format(jumphost, name))

print("\n--- CHECKING COMPLETED ---\n")
table = []
sorted_report = sorted(OrderedDict(report))
for host in sorted_report:
    table.append([host, report[host]])
print(tabulate(table, headers=['Host', 'Status']))
