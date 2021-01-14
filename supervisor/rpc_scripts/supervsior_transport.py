# -*- coding: utf-8 -*-
import urllib.parse as urlparse
from supervisor.rpc_scripts.compat import xmlrpclib
from supervisor.rpc_scripts.compat import urllib
from supervisor.rpc_scripts.compat import httplib
from supervisor.rpc_scripts.compat import as_string
from supervisor.rpc_scripts.compat import as_bytes
from supervisor.rpc_scripts.compat import encodestring
import socket


class UnixStreamHTTPConnection(httplib.HTTPConnection):
    def connect(self): # pragma: no cover
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # we abuse the host parameter as the socketname
        self.sock.connect(self.socketfile)


class SupervisorTransport(xmlrpclib.Transport):
    """
    Provides a Transport for xmlrpclib that uses
    httplib.HTTPConnection in order to support persistent
    connections.  Also support basic auth and UNIX domain socket
    servers.
    """
    connection = None

    def __init__(self, username=None, password=None, serverurl=None):
        xmlrpclib.Transport.__init__(self)
        self.username = username
        self.password = password
        self.verbose = False
        self.serverurl = serverurl
        if serverurl.startswith('http://'):
            type, uri = urllib.splittype(serverurl)
            host, path = urllib.splithost(uri)
            host, port = urllib.splitport(host)
            if port is None:
                port = 80
            else:
                port = int(port)
            def get_connection(host=host, port=port):
                return httplib.HTTPConnection(host, port)
            self._get_connection = get_connection
        elif serverurl.startswith('unix://'):
            def get_connection(serverurl=serverurl):
                # we use 'localhost' here because domain names must be
                # < 64 chars (or we'd use the serverurl filename)
                conn = UnixStreamHTTPConnection('localhost')
                conn.socketfile = serverurl[7:]
                return conn
            self._get_connection = get_connection
        else:
            raise ValueError('Unknown protocol for serverurl %s' % serverurl)

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def request(self, host, handler, request_body, verbose=0):
        request_body = as_bytes(request_body)
        if not self.connection:
            self.connection = self._get_connection()
            self.headers = {
                "User-Agent" : self.user_agent,
                "Content-Type" : "text/xml",
                "Accept": "text/xml"
                }

            # basic auth
            if self.username is not None and self.password is not None:
                unencoded = "%s:%s" % (self.username, self.password)
                encoded = as_string(encodestring(as_bytes(unencoded)))
                encoded = encoded.replace('\n', '')
                encoded = encoded.replace('\012', '')
                self.headers["Authorization"] = "Basic %s" % encoded

        self.headers["Content-Length"] = str(len(request_body))

        self.connection.request('POST', handler, request_body, self.headers)

        r = self.connection.getresponse()

        if r.status != 200:
            self.connection.close()
            self.connection = None
            raise xmlrpclib.ProtocolError(host + handler,
                                          r.status,
                                          r.reason,
                                          '' )
        data = r.read()
        data = as_string(data)
        # on 2.x, the Expat parser doesn't like Unicode which actually
        # contains non-ASCII characters
        data = data.encode('ascii', 'xmlcharrefreplace')
        p, u = self.getparser()
        p.feed(data)
        p.close()
        return u.close()
