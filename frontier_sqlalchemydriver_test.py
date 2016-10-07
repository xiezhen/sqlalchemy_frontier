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
    r = connection.execute('select count(*) as nt from CMS_LUMI_PROD.HFOC_RESULT_4 where RUNNUM=278875 and lsnum>840')
    for row in r:
        print 'test query: ',row['nt']
    rr = connection.execute('select count(*) as nt from CMS_LUMI_PROD.HFOC_RESULT_4 where RUNNUM=:runnum and lsnum>:lsnum',{'runnum':278875,'lsnum':840})

    for row in rr:
        print 'test query with bind: ',row['nt']
        
    q = 'select datatagid,avglumi,fillnum,runnum,lsnum,timestampsec,beamstatusid,cmson,deadtimefrac,datatagnameid,targetegev,numbxbeamactive  from (select i.datatagid as datatagid,i.fillnum as fillnum,i.runnum as runnum,i.lsnum as lsnum,i.timestampsec as timestampsec,i.beamstatusid as beamstatusid,i.cmson as cmson,i.deadtimefrac as deadtimefrac,i.datatagnameid as datatagnameid,b.avglumi as avglumi,f.targetegev as targetegev,f.numbxbeamactive as numbxbeamactive,rank() over(partition by i.runnum,i.lsnum order by i.datatagid desc) rnk from cms_lumi_prod.ids_datatag i, cms_lumi_prod.pltzero_result_4 b, cms_lumi_prod.lhcfill f where i.fillnum=f.fillnum and i.datatagid=b.datatagid and i.runnum=:runmin and i.datatagnameid<=:datatagnameid) where rnk=1 order by runnum,lsnum'
    rrr = connection.execute(q,{'runmin':278875,'datatagnameid': 6144528623329107550})
    for row in rrr:
        print 'test query with rank: ',row['fillnum'],row['runnum'],row['lsnum'],row['timestampsec'],row['cmson'],row['beamstatusid'],row['deadtimefrac'],row['datatagnameid'],row['targetegev'],row['numbxbeamactive']
    connection.close()
    
    

if __name__=='__main__':    
    main()
