from . import Connector
import urllib
import os
import xml.etree.ElementTree as ET

from sqlalchemy import exc

def _buildserverurl(serverlist,proxylist,servlet):
    serverurl = ''
    for s in serverlist:
        pieces = s.split('/')
        pieces[-1] = servlet
        piece = '/'.join(pieces)
        serverurl = serverurl+'(serverurl='+piece+')'
    for p in proxylist:
        serverurl = serverurl+'(proxyurl='+p+')'
    return serverurl

def _frontierconnectparse(filename):
    r = ET.parse(filename)
    root = r.getroot()
    if root.tag == 'frontier-connect':
        frcon = root
    else:
        frcon = root.find('.//frontier-connect')
    servers = frcon.findall('./server')
    server_urls = [x.attrib['url'] for x in servers]
    proxies = frcon.findall('./proxy')
    proxy_urls = [x.attrib['url'] for x in proxies]
    return (server_urls,proxy_urls)

class FrontierConnector(Connector):
    driver = 'frontier'
    
    @classmethod
    def dbapi(cls):
        from sqlalchemy.dialects.oracle import frontier_dbapi
        return frontier_dbapi
        
    def create_connect_args(self, url):
        if url.username or url.password:
            raise exc.ArgumentError(
                "Invalid frontier URL: %s\n"
                "Valid frontier URL forms are:\n"
                " frontier://server:port/servlet\n"
                " frontier:///relative/path/to/site-local-config.xml/servlet\n"
                " frontier:////absolute/path/to/site-local-config.xml/servlet" %(url,)
            )
        server_url = None
        proxy_url = None
        host = url.host
        database = url.database
        port = '8000'
        if host and database:
            if url.port:
                port = url.port
            server_url = 'http://'+urllib.unquote_plus(host)+':'+str(port)+'/'+database
        elif not host and database:
            s = os.path.split(database)
            if len(s)<2:
                 raise exc.ArgumentError(
                      "Invalid SQLite URL: %s\n"
                     "Valid SQLite URL forms are:\n"
                     " oracle+frontier://server:port/site-local-config.xml/servlet\n"
                     " oracle+frontier:///relative/path/to/site-local-config.xml/servlet\n"
                     " oracle+frontier:////absolute/path/to/site-local-config.xml/servlet" % (url,)
                 )
            if not os.path.isabs(s[0]):
                (serverlist,proxylist) = _frontierconnectparse( os.path.abspath(s[0]) )
            else:
                (serverlist,proxylist) = _frontierconnectparse( s[0] )
            database = s[1]
            server_url = _buildserverurl(serverlist,proxylist,database)
            
        else:
            raise exc.ArgumentError(
                "Invalid SQLite URL: %s\n"
                "Valid SQLite URL forms are:\n"
                " oracle+frontier://server:port/site-local-config.xml/database\n"
                " oracle+frontier:///relative/path/to/site-local-config.xml/database\n"
                " oracle+frontier:////absolute/path/to/site-local-config.xml/database" % (url,))        
        self.url_database = database
        print 'self.url_database ',self.url_database        
        print 'server_url ',server_url
        return [
            [server_url,proxy_url],
            {}
        ]       
    
    def do_rollback(self, dbapi_connection):
        pass
    
