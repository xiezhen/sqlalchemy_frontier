import os.path
import ctypes
import logging

me = os.path.abspath(os.path.dirname(__file__))
#libfc = ctypes.cdll.LoadLibrary(os.path.join(me,'..','libfrontier_client.so.2'))
libfc = ctypes.cdll.LoadLibrary(os.path.join(me,'libfrontier_client.so'))
logger = logging.getLogger(__name__)

#wrapped header files: frontier_error.h, frontier.h, frontier-cpp.h

#global defines and constants
FRONTIER_OK        = 0
FRONTIER_EIARG     = -1	
FRONTIER_EMEM      = -2	#mem_alloc failed
FRONTIER_ECFG	   = -3	#config error
FRONTIER_ESYS	   = -4	#system error
FRONTIER_EUNKNOWN  = -5	#unknown error
FRONTIER_ENETWORK  = -6	#error while communicating over network
FRONTIER_EPROTO	   = -7	#protocol level error (e.g. wrong response)
FRONTIER_ESERVER   = -8	#server error (may be cached for short time)
FRONTIER_ECONNECT  = -9	#socket connect error*/

BLOB_BIT_NULL        = 1<<7 #mask
BLOB_TYPE_NONE       = BLOB_BIT_NULL
BLOB_TYPE_BYTE       = 0
BLOB_TYPE_INT4       = 1
BLOB_TYPE_INT8       = 2
BLOB_TYPE_FLOAT      = 3
BLOB_TYPE_DOUBLE     = 4
BLOB_TYPE_TIME       = 5
BLOB_TYPE_ARRAY_BYTE = 6
BLOB_TYPE_EOR        = 7
BLOB_TYPE_NONE       = BLOB_BIT_NULL

FRONTIER_MAX_SERVERN = 16
FRONTIER_MAX_PROXYN = 24
FRONTIER_MAX_PROXYCONFIGN = 8

def _build_frontierRSBlob_get(f):
    def wrapper(rsb):
        retcode = ctypes.c_int(FRONTIER_OK)
        result = f(rsb, ctypes.byref(retcode))
        retcode = retcode.value
        if retcode != FRONTIER_OK:
            raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
        return result
    return wrapper

#functions accept any ctypes data instances as arguments and return the default result type specified by the library loader.

# frontier_error.h frontier_getErrorMsg
frontier_getErrorMsg = libfc.frontier_getErrorMsg
frontier_getErrorMsg.restype = ctypes.c_char_p 

#frontier.h frontierRSBlob_open
frontierRSBlob_open = libfc.frontierRSBlob_open
frontierRSBlob_open.restype = ctypes.c_void_p

#frontier.h frontierRSBlob_close
frontierRSBlob_close = libfc.frontierRSBlob_close
frontierRSBlob_close.restype = None

#frontier.h frontierRSBlob_start
frontierRSBlob_start = libfc.frontierRSBlob_start
frontierRSBlob_start.restype = None

#frontier.h frontierRSBlob_getByte
frontierRSBlob_getByte = libfc.frontierRSBlob_getByte
frontierRSBlob_getByte.restype = ctypes.c_byte

#frontier.h frontierRSBlob_checkByte
frontierRSBlob_checkByte = libfc.frontierRSBlob_checkByte
frontierRSBlob_checkByte.restype = ctypes.c_byte

#frontier.h frontierRSBlob_getInt
frontierRSBlob_getInt = libfc.frontierRSBlob_getInt
frontierRSBlob_getInt.restype = ctypes.c_int

#frontier.h frontierRSBlob_getLong
frontierRSBlob_getLong = libfc.frontierRSBlob_getLong
frontierRSBlob_getLong.restype = ctypes.c_longlong

#frontier.h frontierRSBlob_getDouble
frontierRSBlob_getDouble = libfc.frontierRSBlob_getDouble
frontierRSBlob_getDouble.restype = ctypes.c_double

#frontier.h frontierRSBlob_getFloat
frontierRSBlob_getFloat = libfc.frontierRSBlob_getFloat
frontierRSBlob_getFloat.restype = ctypes.c_float

#frontier.h frontierRSBlob_getByteArray
frontierRSBlob_getByteArray = libfc.frontierRSBlob_getByteArray
frontierRSBlob_getByteArray.restype = ctypes.c_void_p

#frontier.h frontierRSBlob_getRecNum
frontierRSBlob_getRecNum = libfc.frontierRSBlob_getRecNum
frontierRSBlob_getRecNum.restype = ctypes.c_uint

#frontier.h frontierRSBlob_getPos
frontierRSBlob_getPos = libfc.frontierRSBlob_getPos
frontierRSBlob_getPos.restype = ctypes.c_uint

#frontier.h frontierRSBlob_getSize
frontierRSBlob_getSize = libfc.frontierRSBlob_getSize
frontierRSBlob_getSize.restype = ctypes.c_uint

#frontier.h frontierRSBlob_payload_error
frontierRSBlob_payload_error = libfc.frontierRSBlob_payload_error
frontierRSBlob_payload_error.restype = ctypes.c_int

#frontier.h frontierRSBlob_payload_msg
frontierRSBlob_payload_msg = libfc.frontierRSBlob_payload_msg
frontierRSBlob_payload_msg.restype = ctypes.c_char_p

# wrapped functions , objects

class FrontierConfig(ctypes.Structure):            
    _fields_ = [('server', ctypes.c_char_p*FRONTIER_MAX_SERVERN ),('proxy',ctypes.c_char_p*FRONTIER_MAX_PROXYN),('proxyconfig',ctypes.c_char_p*FRONTIER_MAX_PROXYCONFIGN),('server_num',ctypes.c_int),('proxy_num',ctypes.c_int),('proxyconfig_num',ctypes.c_int),('server_cur',ctypes.c_int),('proxy_cur',ctypes.c_int),('proxyconfig_cur',ctypes.c_int),('servers_balanced',ctypes.c_int),('proxies_balanced',ctypes.c_int),('num_backupproxies',ctypes.c_int),('connect_timeout_secs',ctypes.c_int),('read_timeout_secs',ctypes.c_int),('write_timeout_secs',ctypes.c_int),('max_age_secs',ctypes.c_int),('force_reload',ctypes.c_char_p),('freshkey',ctypes.c_char_p),('retrieve_zip_level',ctypes.c_int),('secured',ctypes.c_int),('capath',ctypes.c_char_p),('client_cache_max_result_size',ctypes.c_int),('failover_to_server',ctypes.c_int),('prefer_ip_family',ctypes.c_int)]
    
class FrontierClientError(Exception):
    def __init__(self, retcode, message):
        self.args = (retcode, message)
    
def frontier_createChannel(serverURL = None, proxyURL = None):
    logger.debug('frontier_client.frontier_createChannel(serverURL = %s, proxyURL = %s)', repr(serverURL), repr(proxyURL) )
    retcode = ctypes.c_int(FRONTIER_OK)
    channel = libfc.frontier_createChannel(serverURL, proxyURL, ctypes.byref(retcode))
    retcode = retcode.value
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
    logger.debug('frontier_client.frontier_createChannel(serverURL = %s, proxyURL = %s) = %s', repr(serverURL), repr(proxyURL), channel)
    return channel

#frontier_config.h frontierConfig_get
frontierConfig_get = libfc.frontierConfig_get
frontierRSBlob_payload_msg.restype = ctypes.POINTER(FrontierConfig)

frontierConfig_addServer = libfc.frontierConfig_addServer
frontierConfig_addServer.restype = ctypes.c_int

frontierConfig_addProxy = libfc.frontierConfig_addProxy
frontierConfig_addProxy.restype = ctypes.c_int


def frontierConfig_addServer(fconfig, serverURL):
    retcode = ctypes.c_int(FRONTIER_OK)
    pos = libfc.frontierConfig_addServer( ctype.byref(fconfig), serverURL)
    retcode = retcode.value
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
    logger.debug('frontier_client.frontierConfig_addServer(serverURL = %s) = %s', repr(serverURL), pos)
    return pos

def frontierConfig_addProxy(fconfig, proxyURL):
    retcode = ctypes.c_int(FRONTIER_OK)
    pos = libfc.frontierConfig_addProxy( ctype.byref(fconfig), proxyURL)
    retcode = retcode.value
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
    logger.debug('frontier_client.frontierConfig_addServer(proxyURL = %s) = %s', repr(proxyURL), pos)
    return pos
    
#def frontier_createChannel2(serverURLs = [], proxyURLs = []):
#    retcode = ctypes.c_int(FRONTIER_OK)
#    #fconfig = FrontierConfig()
#    #fconfig.server[:] = (ctypes.c_char_p*FRONTIER_MAX_SERVERN)()
#    #fconfig.server_num = len(serverURLs)
#    #fconfig.proxy[:] = (ctypes.c_char_p*FRONTIER_MAX_PROXYN)()
#    #fconfig.proxy_num = len(proxyURLs)
#    #print serverURLs
#    print 11
#    for serverURL in serverURLs:        
#    channel = libfc.frontier_createChannel2( ctypes.byref(fconfig), ctypes.byref(retcode) )
#    print 22
#    retcode = retcode.value
#    if retcode != FRONTIER_OK:
#        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
#    logger.debug('frontier_client.frontier_createChannel2(serverURLs = %s, proxyURLs = %s) = %s', repr(serverURLs), repr(proxyURLs), channel)
#    return channel

def frontier_closeChannel(channel):
    logger.debug('frontier_client.frontier_closeChannel(channel = %s)', repr(channel) )
    libfc.frontier_closeChannel(channel)

def frontier_getRawData(channel, uri):
    logger.debug('frontier_client.frontier_getRawData(channel = %s, uri = %s)', repr(channel), repr(uri) )
    retcode = libfc.frontier_getRawData(channel, uri)
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())

def frontierRSBlob_open(channel, oldrs, n):
    logger.debug('frontier_client.frontierRSBlob_open(channel = %s, oldrs = %s, n = %s)', channel, oldrs, n )
    retcode = ctypes.c_int(FRONTIER_OK)
    rs = libfc.frontierRSBlob_open(channel, oldrs, n, ctypes.byref(retcode) )
    retcode =  retcode.value
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
    retcode = libfc.frontierRSBlob_payload_error(rs)
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontierRSBlob_payload_msg(rs))
    return rs

def frontierRSBlob_close(rs):
    logger.debug('frontier_client.frontierRSBlob_close(rs = %s)', rs)
    retcode = ctypes.c_int(FRONTIER_OK)
    libfc.frontierRSBlob_close(rs, ctypes.byref(retcode) )
    retcode = retcode.value
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())

frontierRSBlob_getByte = _build_frontierRSBlob_get(libfc.frontierRSBlob_getByte)
frontierRSBlob_checkByte = _build_frontierRSBlob_get(libfc.frontierRSBlob_checkByte)
frontierRSBlob_getInt = _build_frontierRSBlob_get(libfc.frontierRSBlob_getInt)
frontierRSBlob_getLong = _build_frontierRSBlob_get(libfc.frontierRSBlob_getLong)
frontierRSBlob_getDouble = _build_frontierRSBlob_get(libfc.frontierRSBlob_getDouble)
frontierRSBlob_getFloat = _build_frontierRSBlob_get(libfc.frontierRSBlob_getFloat)


def frontierRSBlob_getByteArray(rs):
    buflen = frontierRSBlob_getInt(rs)
    retcode = ctypes.c_int(FRONTIER_OK)
    buf = libfc.frontierRSBlob_getByteArray(rs, buflen, ctypes.byref(retcode))
    retcode = retcode.value
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
    s = ctypes.string_at(buf, buflen)
    return s

def frontierRSBlob_getRecNum(rs):
    '''
    get number of returned records
    '''
    logger.debug('frontier_client.frontierRSBlob_getRecNum(rs = %s)', rs )
    return libfc.frontierRSBlob_getRecNum(rs)

def frontier_mem_free(address):
    '''
    C.in_dll(dll, name) access a C ubstabce in a dll 
    '''
    ctypes.CFUNCTYPE(None, ctypes.c_void_p)(ctypes.c_void_p.in_dll(libfc, 'frontier_mem_free').value)(address)

def fn_gzip_str2urlenc(string):
    '''
    gzip string then 64base encode to ascii 
    fn-zlib.c
    '''
    logger.debug('frontier_client.fn_gzip_str2urlenc(string = %s)', repr(string))
    buf = ctypes.c_void_p()
    buflen = libfc.fn_gzip_str2urlenc(string, len(string), ctypes.byref(buf))
    if buflen < 0 :
        raise FrontierClientError(None, 'Impossible to encode.')
    s = ctypes.string_at(buf.value, buflen)
    frontier_mem_free(buf.value)
    return s
    
def frontier_init():
    logger.debug('frontier_client.frontier_init()')
    logger.debug('AAA')
    retcode = libfc.frontier_init(None, None)
    logger.debug('retcode '+str(retcode))
    if retcode != FRONTIER_OK:
        raise FrontierClientError(retcode, libfc.frontier_getErrorMsg())
logger.debug('about to init')
frontier_init()
logger.debug('after init')