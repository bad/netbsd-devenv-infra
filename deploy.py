# -*- python -*-
# manage standard config files on nbvm

import os, platform
import functools

# from pyinfra import config
from pyinfra import host
from pyinfra.operations import files, server

@functools.cache                # probably over-optimized but more correct
                                # as we're interested in the value "at
                                # startup."
def local_hostname():
    """return the hostname of the machine running pyinfra"""
    # allow the hostname to be overridden.
    # strip any attached domain suffix
    # c.f. https://stackoverflow.com/questions/4271740#comment73605463_4271873
    os.getenv('HOSTNAME',os.getenv('COMPUTERNAME',
                                    platform.node())).split('.')[0]

if 'asroot' in host.groups:
    for f in ("shrc", "login.conf"):
        d=f'/etc/{f}'
        files.put(
            name=f'Ensure {d}',
            dest=d,
            src=f'files/etc.{f}',
        )

    f = "/etc/sysctl.conf"
    sysctl_cnf = files.line(
        name=f'Ensure ddb.onpanic=1 in {f}',
        path=f,
        line=r"^ddb.onpanic.*",
        replace="ddb.onpanic?=1",
        ensure_newline=True,
    )
    f = "/etc/hosts"
    for addr in ("fec0::2", "10.0.2.2",):
        files.line(
            name=f'address {addr} for VM host in {f}',
            path=f,
            line=f'^{addr}\\s+host$',
            replace=f'{addr} 		host',
            present=True,
        )
    server.shell(
        name='Apply /etc/sysctl.conf',
        commands="/etc/rc.d/sysctl start",
        _if=sysctl_cnf.did_change,
    )

if 'asuser' in host.groups:
    for f in ['exrc', 'gdbinit', 'shrc',]:
        files.put(
            name=f'Ensure ~/.{f}',
            dest=f'.{f}',
            src=f'files/{f}',
        )
