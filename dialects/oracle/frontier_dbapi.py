'''
This module implements the Python Database API Specification V2.0, http://www.python.org/dev/peps/pep-0249
'''

import exceptions
import datetime
import time
import re
import collections
import logging
import frontier_client_ctypes as frontier_client
import ctypes

try:
    import pytz
except ImportError:
    pytz = None
    
#Globals
#These module globals must be defined

apilevel = '2.0'
threadsafety = 1     #Threads may share the module, but not connections.
paramstyle = 'named' #Named style, e.g. ...WHERE name=:name

_paramchar = '?'
_separatorchar = ':'

Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime
Binary = buffer

logger = logging.getLogger(__name__)

# Set initial level to WARN. This so that log statements don't occur in the absense of explicit logging being enabled

if logger.level == logging.NOTSET:
    logger.setLevel(logging.WARN)

def connect(server_url = None, proxy_url = None):
    '''
    connect method is the entry point to the module.
    It takes any arguments
    Returns a Connection object
    
    The connection will be configured according to:

      1. The environment variables defined by Frontier
      2. The passed URLs.

      Note that the server_url (and its environment variable counterpart) can be a simple HTTP URL or a complex Frontier configuration URL that sets man configuration values, e.g.
      
          frontier://(k1=v1)...(kn=vn)/database

    While this complex URLs are the most used ones, users normally do not directly use them. Instead, they will use an experiment-provided application or service that builds them given a shorthand name.

    For instance, in CMS, a user could run:
     
     frontier://FrontierPrep

    Since this module should remain experiment-agnostic, users need to supply the proper way to fetch the complex URLs.
    '''    
    return Connection(server_url,proxy_url)

#Exceptions

class Error(exceptions.StandardError):
    pass

class Warning(exceptions.StandardError):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DataError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class InternalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass

#Connection Objects
class Connection(object):
    def __init__(self, server_url, proxy_url=None):
        self._closed = False
        self._server_url = server_url
        self._proxy_url = proxy_url
        self._channel = frontier_client.frontier_createChannel(self._server_url, self._proxy_url)
        
    def _check_closed(self):
        if self._closed:
            raise InterfaceError('The connection is already closed.')
        
    def close(self):
        '''
        Close the connection now (rather than whenever .__del__() is called).
        
        '''
        self._check_closed()
        self._closed = True
        frontier_client.frontier_closeChannel(self._channel)

    def commit(self):
        '''
        Commit any pending transaction to the database.
        '''
        self._check_closed()

    def cursor(self):
        '''
        Return a new Cursor Object using the connection.
        '''
        self._check_closed()
        return Cursor(self)

def _stringify(parameter):
    if parameter is None:
        return 'NULL'
    elif isinstance(parameter, bool):
        if parameter:
            return 'TRUE'
        else:
            return 'FALSE'
    elif isinstance(parameter, str):
        return parameter
    elif isinstance(parameter, int) or isinstance(parameter, long) or isinstance(parameter, float):
        return str(parameter)
    raise ProgrammingError('Unsupported parameter type (%s).'% type(parameter))
    
def _parse_timestamp(timestamp):
    try:
        return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    
#Cursor Objects
class Cursor(object):
    arraysize = 1    

    def _reset(self):
        self._description = None
        self._rowcount = -1
        self._result = None
        self._rowpos = None

    def _check_closed(self):
        if self._closed:
            raise InterfaceError('The connection is already closed.')
        self._connection._check_closed()
        
    def _check_result(self):
        logger.debug('Cursor._check_result')
        if self._result is None:
            raise InterfaceError('Fetched from a cursor without executing a query first')
        
    def _fetchone(self, parse):
        row = []
        i = -1
        while True:
            i += 1
            data_type = frontier_client.frontierRSBlob_getByte(self._result)
            #End
            if data_type == frontier_client.BLOB_TYPE_EOR:
                break
            #NULL
            if data_type & frontier_client.BLOB_TYPE_NONE:
                row.append(None)
                continue
            value = frontier_client.frontierRSBlob_getByteArray(self._result)
            if parse:
                columnType = self._description[i][1]
                if 'CHAR' in columnType or columnType == 'ROWID':
                    pass                
                elif columnType.startswith('NUMBER'):
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                elif columnType.startswith('BINARY_FLOAT') or columnType.startswith('BINARY_DOUBLE'):
                    value = float(value)
                elif columnType in ('BLOB', 'CLOB'):
                    value = Binary(value)
                elif columnType == 'DATE':
                    value = _parse_timestamp(value)
                elif columnType.startswith('TIMESTAMP'):
                    if 'WITH TIME ZONE' in columnType:
                        if pytz is None:
                            raise InterfaceError('Query returned a timezone-aware timestamp, but the pytz module is not available.')
                        (timeString, timeZone) = value.rsplit(' ',1)
                        value = pytz.timezone(timeZone).localize(_parse_timestamp(timeString))
                    elif 'WITH LOCAL TIMEZONE' in columnType:
                        raise NotSupportedError('Unsupported type (%s).' % columnType)
                    else:
                        value = _parse_timestamp(value)
                else:
                    raise NotSupportedError('Unsupported type (%s). '% columnType)
            row.append(value)
        return row

    @property
    def description(self):
        '''
        name,type_code,display_size,internal_size,precision,scale,null_ok
        '''
        self._check_closed()
        return self._description
    
    @property 
    def rowcount(self):
        self._check_closed()
        return self._rowcount
    
    def __init__(self,connection):
        self._connection = connection
        self._closed = False
        self._reset()

    def callproc(self,procname):
        pass
    def close(self):
        self._check_closed()
        self._closed = True
        
    def execute(self, operation, parameters=None ):
        '''
        Prepare and execute a database operation (query or command).
        '''
        self._check_closed()
        variables = re.findall(':[a-zA-Z-0-9_]+', operation)
        logger.debug('Variables = %s', variables)
        
        final_parameters = []
        if parameters is None:
            if len(variables) != 0:
                raise ProgrammingError('Bind variables used, but parameters were not provided')
        elif isinstance(parameters, collections.Sequence) :
            if len(parameters) != len(variables):
                raise ProgrammingError('Different length on parameters (%s) and bind variables list (%s) while using positional parameters.' %(len(parameters), len(variables)))

                for i in range(len(variables)):
                    operation = operation.replace(variables[i], _paramchar, 1) 
                    final_parameters = parameters
        elif isinstance(parameters, collections.Mapping):
            for variable in variables:
                operation = operation.replace(variable, _paramchar, 1)
                final_parameters.append(parameters[variable[1:]])
        else:
            raise ProgrammingError('Unsupported parameters type (%s).'%type(parameters))
        final_parameters = [_stringify(x) for x in final_parameters]
        for parameter in final_parameters:
            if _separatorchar in parameter:
                raise ProgrammingError("Unsupported character '%s' in parameter(%s)." %(_separatorchar, parameter))

        logger.info('%s', operation)
        logger.info('%s', final_parameters)

        operation = _separatorchar.join([operation] + final_parameters)
        logger.debug('Query to Frontier = %s', operation)
        
        # Build the URI
        uri = 'Frontier/type=frontier_request:1:DEFAULT&encoding=BLOBzip5&p1=%s'%frontier_client.fn_gzip_str2urlenc(operation)
        try:
            frontier_client.frontier_getRawData(self._connection._channel, uri)
        except frontier_client.FrontierClientError as e:
            self._reset()
            raise ProgrammingError('Error while fetching data: %s' %e)
        oldresult = self._result
        self._result = frontier_client.frontierRSBlob_open(self._connection._channel, self._result, 1)
        if oldresult:
            frontier_client.frontierRSBlob_close(oldresult)                
        self._rowcount = frontier_client.frontierRSBlob_getRecNum(self._result)
        row = self._fetchone(parse = False)
        self._description = []
        for i in range(0, len(row), 2):
            # name, type, display_size, internal_size, precision, scale, null_ok
            self._description.append( (row[i], row[i+1], None, None, None, None, None) )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('Col %s', [x[0] for x in self._description])
        self._rowpos = 0
            
    def executemany(self, operation, seq_of_parameters ):
        '''
        Prepare a database operation (query or command) and then execute it against all parameter sequences or mappings found in the sequence seq_of_parameters .
        '''
        self._check_closed()

    def fetchone(self):
        '''
        Fetch the next row of a query result set, returning a single sequence, or None when no more data is available. [6]  
        '''
        self._check_closed()
        self._check_result()

        if self._rowpos == self._rowcount:
            return None
        self._rowpos += 1

        row = self._fetchone(parse = True)
        if len(self._description) != len(row):
            raise InternalError('Row description length (%s) does not match number of columns in row (%s)' %(len(self._description), len(row)))
        logger.debug('Row %s', row)
        return row

    def fetchmany(self, size=arraysize):
        '''
        Fetch the next set of rows of a query result, returning a sequence of sequences (e.g. a list of tuples). An empty sequence is returned when no more rows are available.
        '''
        self._check_closed()
        self._check_result()

        result = []
        for n in range(size):
            row = self.fetchone()
            if row is None:
                break
            result.append(row)            
        return result

    def fetchall(self):
        '''
        Fetch all (remaining) rows of a query result, returning them as a sequence of sequences (e.g. a list of tuples). Note that the cursor's arraysize attribute can affect the performance of this operation.
        '''
        self._check_closed()
        self._check_result()

        result = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            result.append(row)            
        return result
    
    def nextset(self):
        self._check_closed()

    def setinputsize(self, sizes):
        self._check_closed()

    def setoutputsize(self, size, column=None):
        self._check_closed()    
    
    def DateFromTicks(ticks):
        return Date(*time.localtime(ticks)[:3])
    def TimeFromTicks(ticks):
        return Time(*time.localtime(ticks)[3:6])
    def TimestampFromTicks(ticks):
        return Timestamp(*time.localtime(ticks)[:6])

    
    
