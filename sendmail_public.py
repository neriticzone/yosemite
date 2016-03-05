import requests
from BeautifulSoup import BeautifulSoup
from pandas import date_range
import MySQLdb as mdb
import smtplib

def spool():
    select = ("select distinct u.name, u.email, DATE_FORMAT(u.start_date, '%m/%d/%Y'), u.duration, u.status, u.id,s.campground "
    " from users u, "
    " sites s "
    " where s.real_date = u.start_date "
    " and s.available = 1 "
    " and u.status = 1"
    " and u.duration = (select count(available) "
    " from sites a "
    " where a.campground = s.campground "
    " and a.site = s.site "
    " and a.available = 1 "
    " and a.real_date between s.real_date and s.real_date + interval u.duration DAY); ")

    #name, email, start_date, duration, status, id, campground
    con = mdb.connect('mysql.server', 'XXXXX', 'XXXXXX', 'XXXXXXXXX')
    c = con.cursor()
    c.execute(select)
    c.fetchall()
    grounds = {"70928" : "Lower Pines","70925":"Upper Pines","70927": "North Pines"}
    for i in c:
        print i
        message = ("Hi %s! A Yosemite Campsite has been found with your specifications! \n"
        "Campground: %r \n"
        "Date: %r \n"
        "Duration: %r nights \n"
        "Click on the link below to view available site(s)! \n"
        "http://www.recreation.gov/campsiteCalendar.do?page=matrix&contractCode=NRSO&parkId=%r&calarvdate=%s"%(i[0],grounds[str(i[6])],i[2],i[3],int(i[6]),i[2]))

        subject = "Yosemite Campsite Found!"
        send_email(1,i[1],subject,message)
        try:
            print "delete from users where id = %r ;" %(int(i[5]))
            c.execute("delete from users where id = %r ;" %(int(i[5])))
            con.commit();
        except mdb.Error as e:
            print e.args
            print "exiting inserts"
            return 0

    con.close()

def send_email(id,mail_id,subject,message):
    gmail_user = "XXXXXXXXXX"
    gmail_pwd = "XXXXXXXXXX"
    FROM = 'XXXXXXXXXXXXXXXXXX'
    TO = [str(mail_id)] #must be a list
    SUBJECT = subject
    TEXT = message
    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    #server.quit()
    server.close()
    return 1

	#lower pines 70928
	#upper piines 70925
	#north pines 70927
