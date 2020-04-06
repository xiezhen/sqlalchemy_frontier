from . import Connector
import urllib
import os
import xml.etree.ElementTree as ET

from sqlalchemy import exc

def _buildserverurl(configdict,servlet):
    serverurl = ''
    for k,vlist in configdict.items():
        for value in vlist:
            if k=='serverurl':
                pieces = value.split('/')
                pieces[-1] = servlet
                piece = '/'.join(pieces)
                serverurl = serverurl+'(serverurl='+piece+')'
            else:
                serverurl = serverurl+'(%s='%(k)+value+')'    
    #print 'serverurl ',serverurl
    return serverurl

def _frontierconnectparse(filename):
    r = ET.parse(filename)
    root = r.getroot()
    result = {}
    if root.tag == 'frontier-connect':
        frcon = root
    else:
        frcon = root.find('.//frontier-connect')
    for child in frcon:
        attrname = list(child.attrib)[0]
        result.setdefault(child.tag+attrname,[]).append(child.attrib[attrname])
    return result

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
            server_url = 'http://'+urllib.parse.unquote_plus(host)+':'+str(port)+'/'+database
        elif not host and database:
            s = os.path.split(database)
            if len(s)<2 or not s[0] or not s[1]:
                 raise exc.ArgumentError(
                      "Invalid frontier URL: %s\n"
                     "Valid frontier URL forms are:\n"
                     " oracle+frontier://server:port/site-local-config.xml/servlet\n"
                     " oracle+frontier:///relative/path/to/site-local-config.xml/servlet\n"
                     " oracle+frontier:////absolute/path/to/site-local-config.xml/servlet" % (url,)
                 )            
            if not os.path.isabs(s[0]):
                if os.path.isfile(s[0]):
                    frontierconfig_dict = _frontierconnectparse( os.path.abspath(s[0]) )
                else:
                    raise exc.ArgumentError("Invalid frontier config file %s"%(s[0]) )
            else:
                frontierconfig_dict = _frontierconnectparse( s[0] )
            database = s[1]
            server_url = _buildserverurl(frontierconfig_dict,database)
            
        else:
            raise exc.ArgumentError(
                "Invalid frontier URL: %s\n"
                "Valid frontier URL forms are:\n"
                " oracle+frontier://server:port/site-local-config.xml/database\n"
                " oracle+frontier:///relative/path/to/site-local-config.xml/database\n"
                " oracle+frontier:////absolute/path/to/site-local-config.xml/database" % (url,))        
        self.url_database = database
        return [
            [server_url,proxy_url],
            {}
        ]       
    
    def do_rollback(self, dbapi_connection):
        pass
    
