from . import Connector
import urllib

class FrontierConnector(Connector):
    driver = 'frontier'
    
    @classmethod
    def dbapi(cls):
        #return  __import__('frontier_dbapi')
        from sqlalchemy.dialects.oracle import frontier_dbapi
        return frontier_dbapi
        
    def create_connect_args(self, url):
        self.url_database = url.database        
        return [
            [urllib.unquote_plus(url.host)] if url.host else [],
            url.query
            ]
    
    def do_rollback(self, dbapi_connection):
        pass
    
