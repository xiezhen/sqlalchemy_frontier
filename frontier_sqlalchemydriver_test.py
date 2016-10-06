from sqlalchemy import create_engine

import logging
import sys
def main():
    logging.basicConfig(level = logging.DEBUG)   
    #urlstr = 'oracle+frontier://cmsfrontier.cern.ch:8000/LumiCalc+/cmsfrontier1.cern.ch:8000/LumiCalc'
    #proxy = 'http://cmst0frontier.cern.ch:3128'
    #complexurl = '(serverurl=http://cmsfrontier.cern.ch:8000/LumiCalc)(serverurl=http://cmsfrontier3.cern.ch:8000/LumiCalc)(serverurl=http://cmsfrontier4.cern.ch:8000/LumiCalc)(proxyurl=http://cmst0frontier.cern.ch:3128)'
    #connection = frontier.Connection(server_url=url, proxy_url=proxy) #one one case only
    #connection = frontier.Connection(server_url=complexurl)
    
    #cursor1 = connection.cursor()
    #cursor1.execute('select 1 from dual')
    #cursor1.execute("select count(*) as nt from CMS_LUMI_PROD.HFOC_RESULT_4 where RUNNUM=278875 and lsnum>840")
    #print cursor1.fetchall()
    #result = cursor1.fetchone()[0]
    #cursor1.close()
    #connection.close()
    urlstr = 'oracle+frontier://cmsfrontier.cern.ch:8000/LumiCalc'
    #urlstr = 'oracle+frontier:///site-local-config.xml/LumiCalc'
    engine = create_engine(urlstr)
    connection = engine.connect()
    engine.execute('select 1 from dual')
    connection.close()

    

if __name__=='__main__':    
    main()
