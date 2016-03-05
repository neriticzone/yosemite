import requests
from BeautifulSoup import BeautifulSoup
from pandas import date_range
import MySQLdb as mdb

def scrape():
    #enter your own db information
    con = mdb.connect('mysql.server', 'XXXX', 'XXXXX', 'XXXXX')
    c = con.cursor()
    c.execute("delete from sites;")
    con.commit()
    con.close()
    x = date_range(start = '1/1/2016', end = '12/31/2016',freq = '14D')
    y = [str(z.month)+'/'+str(z.day)+'/'+str(z.year) for z in x ]
    #lower pines 70928
    #upper piines 70925
    #north pines 70927
    sites = ['70928','70925','70927']
    result = []
    translate = []
    for p in sites:
        for g in y:
            url = 'http://www.recreation.gov/campsiteCalendar.do?page=matrix&contractCode=NRSO&parkId='+p+'&calarvdate='+g
            response = requests.get(url)
            html = response.content

            soup = BeautifulSoup(html)
            table = soup.find('table',id = 'calendar')
            # print table
            rows = []
            i = 0
            try:
                for row in table.findAll('tr'):
                    if row.text.find('Map') > -1 and p == '70928':
                        rows.append([row.text[3:6]]+list(row.text[8:]))

                    elif row.text.find('Map') > -1 and p == '70925':
                        rows.append([row.text[3:6]]+list(row.text[17:]))
                    
                    elif row.text.find('Map') > -1 and p == '70927':
                        rows.append([row.text[3:6]]+list(row.text[11:]))
                    
            except:
                pass
            for j in rows:
                # print [p]+[g]+[j[0]]+[1 if x=='A' else 0 for x in j[1:]]
                # stopper = input("pausing for value read")
                translate.append([p]+[g]+[j[0]]+[1 if x=='A' else 0 for x in j[1:]])


    print len(translate)
    count = 0
    try:
        con = mdb.connect('mysql.server',  'XXXX', 'XXXXX', 'XXXXX')
        c = con.cursor()
    except mdb.Error as e:
        print e.args
        print "exiting inserts"
        return 0
    for i in translate:
        #print "HELLO" + i[2]
        x = date_range(start = i[1], periods=14,freq = '1D')
        y = [str(z.month)+'/'+str(z.day)+'/'+str(z.year) for z in x ]
        campground = i[0]
        site = i[3]
        for j in range(0,14):
            sqls = "insert into sites (campground,site,date,available) values (%r,%r,%r,%r);"%(i[0],str(i[2]),y[j],i[3+j])
            try:
                c.execute(sqls)
                con.commit()
                count = count + 1
            except mdb.Error as e:
                print e.args

    c.execute("update sites set real_date = str_to_date(date,'%m/%d/%Y');")
    con.commit()
    con.close()
    print str(count) + " rows inserted"

