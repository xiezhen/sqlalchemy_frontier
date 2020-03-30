'''
  .. dialect:: oracle+frontier
      :name: Frontier
      :dbapi: frontier
      :connectstring: oracle+frontier://@serverURL[/dbname]
      :driverurl: http://frontier.cern.ch
'''

from sqlalchemy.connectors.frontier import FrontierConnector
from sqlalchemy.dialects.oracle.base import OracleCompiler, OracleDialect

class OracleCompiler_frontier(OracleCompiler):
    def __init__(self, *args, **kwargs):
        super(OracleCompiler_frontier, self).__init__(*args, **kwargs)

    def visit_table(self, table, asfrom=False, iscrud=False, ashint=False, fromhints=None, **kwargs):
        if asfrom or ashint:
            if getattr(table, "schema", None):
                ret = self.prepare.quote_schema(table.schema, table.quote_schema) + "." + self.preparer.quote(table.name, table.quote)
            elif self.dialect.default_schema_name:
                ret = self.prepare.quote_schema(table.dialect.default_schema_name, table.quote_schema) + "." + self.preparer.quote(table.name, table.quote)
            else:
                ret = self.preparer.quote(table.name, table.quote)
            if fromhints and table in fromhints:
                ret = self.format_from_hint_text(ret, table, fromhints[table], iscrud)
            return ret
        else:
            return ""

class OracleDialect_frontier(FrontierConnector, OracleDialect):
    
    statement_compiler = OracleCompiler_frontier
    def _get_default_schema_name(self, connection):
        return self.url_database
    def _get_server_version_info(self, connection):
        return (9,0)
dialect = OracleDialect_frontier
