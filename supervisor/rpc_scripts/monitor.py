# -*- coding: utf-8 -*-
from supervisor.rpc_scripts.supervsior_transport import SupervisorTransport
from xmlrpc.client import ServerProxy


class SupervisorMonitor:

    def __init__(self, conf):
        self.user = conf['username']
        self.password = conf['password']
        self.host = conf['host']
        self.port = conf['port']
        rpc_address = 'http://{host}:{port}'.format(host=self.host, port=self.port)
        transport = SupervisorTransport(self.user, self.password, rpc_address)
        self.server = ServerProxy(uri=rpc_address, transport=transport)

    def getSupervisorVersion(self):
        return self.server.supervisor.getSupervisorVersion()

    def listMethods(self):
        return self.server.system.listMethods()

    def methodHelp(self, method):
        return self.server.system.methodHelp(method)

    def getProcessInfo(self, process):
        return self.server.supervisor.getProcessInfo(process)

    def get_process_config_file(self):
        return self.server.supervisor.get_process_config_file()

    def addProcessGroup(self, name, cmd):
        return self.server.supervisor.addProcessGroup(name, cmd)

    def getAllConfigInfo(self):
        return self.server.supervisor.getAllConfigInfo()

    def readProcessStdoutLog(self, name, offset, length):
        return self.server.supervisor.readProcessStdoutLog(name, offset, length)

    def readProcessLog(self, name, offset, length):
        return self.server.supervisor.readProcessLog(name, offset, length)

    def startProcess(self, name):
        return self.server.supervisor.startProcess(name)

    def stopProcess(self, name):
        return self.server.supervisor.stopProcess(name)

    def restartProcess(self, name):
        try:
            response = self.server.system.listMethods()
        except:
            print('{}：SupervisorRPC异常'.format(self.host))
            return

        if self.getProcessInfo(name)['statename'] == 'RUNNING':
            r = self.server.supervisor.stopProcess(name)
            print('{}: StopProcess , 成功更新 {}'.format(self.host, name))
            if r:
                self.startProcess(name=name)
                print('{}：StartProcess , 成功更新 {}'.format(self.host, name))
        else:
            self.startProcess(name=name)
            print('{}：StartProcess , 成功更新 {}'.format(self.host, name))

    def auto_config(self, name, cmd, force_replace=False):
        if not force_replace:
            process_list = self.get_process_config_file()
            if name in process_list:
                raise ValueError('存在相同命名！请重新为程序命名或force_replace=true')
        return self.server.supervisor.auto_config(name, cmd)

    def auto_run(self, name, cmd, force_replace=False):
        if not force_replace:
            process_list = self.get_process_config_file()
            if name in process_list:
                raise ValueError('存在相同命名！请重新为程序命名或force_replace=true')
        return self.server.supervisor.auto_run(name, cmd)
