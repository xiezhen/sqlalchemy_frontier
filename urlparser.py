import re
import os.path

from urllib.parse import unquote
import xml.etree.ElementTree as ET

def make_url(name_or_url):
    """Given a string or unicode instance, produce a new URL instance.

    The given string is parsed according to the RFC 1738 spec.  If an
    existing URL object is passed, just returns the object.
    """

    if isinstance(name_or_url, str):
        return _parse_rfc1738_args(name_or_url)
    else:
        return name_or_url


def _parse_rfc1738_args(name):
    pattern = re.compile(r'''
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>.*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )?
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<database>.*))?
            ''', re.X)

    m = pattern.match(name)
    if m is not None:
        components = m.groupdict()
        if components['database'] is not None:
            tokens = components['database'].split('?', 2)
            components['database'] = tokens[0]
            query = None
            #query = (
            #    len(tokens) > 1 and dict(util.parse_qsl(tokens[1]))) or None
            #if util.py2k and query is not None:
            #    query = dict((k.encode('ascii'), query[k]) for k in query)
        else:
            query = None
        components['query'] = query

        if components['username'] is not None:
            components['username'] = _rfc_1738_unquote(components['username'])

        if components['password'] is not None:
            components['password'] = _rfc_1738_unquote(components['password'])

        ipv4host = components.pop('ipv4host')
        ipv6host = components.pop('ipv6host')
        components['host'] = ipv4host or ipv6host
        name = components.pop('name')
        return (name, components)
    else:
        raise exc.ArgumentError(
            "Could not parse rfc1738 URL from string '%s'" % name)


def _rfc_1738_quote(text):
    return re.sub(r'[:@/]', lambda m: "%%%X" % ord(m.group(0)), text)


def _rfc_1738_unquote(text):
    return unquote(text)

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

if __name__=='__main__':
    e = 'frontier://cmsfrontier.cern.ch:8000/LumiCalc'
    print(e,make_url(e))
        
    b = 'frontier:///x/d/d/site-local-config.xml/LumiCalc'
    print(b,make_url(b))
    c = 'frontier:////absolute/path/to/site-local-config.xml/LumiCalc'
    print(c,make_url(c))

    print(_frontierconnectparse('site-local-config.xml'))
   
    #d = 'frontier://@(serverurl=http://cmsfrontier.cern.ch:8000/LumiCalc)(serverurl=http://cmsfrontier3.cern.ch:8000/LumiCalc)(serverurl=http://cmsfrontier4.cern.ch:8000/LumiCalc)(proxyurl=http://cmst0frontier.cern.ch:3128)'
    
    #dd = list(d)
    #b = make_url(dd)
    #print ''.join(b)
