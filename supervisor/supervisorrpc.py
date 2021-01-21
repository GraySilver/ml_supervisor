# -*- coding: utf-8 -*-
import argparse
import sys
from supervisor.rpc_scripts.monitor import SupervisorMonitor


def main():
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', type=str, default='127.0.0.1', help='host')
    parser.add_argument('-p', default='9001', help='port')
    parser.add_argument('-u', default=None, help='username')
    parser.add_argument('-passwd', default=None, help='passwd')
    parser.add_argument('-task', choices=['config', 'run'], help='can choose `config` or `run` cmd')
    parser.add_argument('-name', help='a supervisor program name')
    parser.add_argument('-cmd', help='supervisor program cmd')
    parser.add_argument('-force', type=bool, default=False, help='if you want to replace program, set true')

    args = parser.parse_args()
    passwd = args.passwd
    cmd = args.cmd
    host = args.host
    port = args.p
    username = args.u
    task = args.task
    name = args.name
    force = args.force
    sm = SupervisorMonitor(username=username, port=port, host=host, password=passwd)

    if task == 'config':
        if name is None or cmd is None:
            raise ValueError('`name` or `cmd` set value.')
        return sm.auto_config(name=name, cmd=cmd, force_replace=force)
    elif task == 'run':
        if name is None or cmd is None:
            raise ValueError('`name` or `cmd` set value.')
        return sm.auto_run(name=name, cmd=cmd, force_replace=force)
    else:
        raise ValueError('`task` should in (config, run).')

if __name__ == '__main__':
    main()
