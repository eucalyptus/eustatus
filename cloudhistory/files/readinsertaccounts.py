#!/usr/bin/python
#
#  Python script to read tidied and stripped xml from euare-accountlist --debug to postgres DB as an eemon user
#
import sys
import string
import psycopg2
import datetime
import StringIO
from xml.etree.ElementTree import iterparse
import argparse
import subprocess
import StringIO


sampledatetime = datetime.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument('-n','--databasename')
parser.add_argument('-p','--databasepassword')
parser.add_argument('-port','--databaseport',default ="5432")
parser.add_argument('-u','--databaseusername',default = 'eemon')
parser.add_argument('-x','--pathtotidyxmlfile', required=True)

args = parser.parse_args()

database=args.databasename
dbPasswd=args.databasepassword
dbPort=args.databaseport
dbUser=args.databaseusername
cloudhistoryxmlpath=args.pathtotidyxmlfile

#print "name pw port user xml",database,dbPasswd,dbPort,dbUser,cloudhistoryxmlpath
#exit()

# account id
AccountId = ''
# Account name
AccountName = ''
# Account email
AccountEmail = ''

def getEmail(AccountName):
        command3 = "euare-usergetinfo -u " + AccountName + " -k email --delegate=" + AccountName
        proc3 = subprocess.Popen(command3, stdout=subprocess.PIPE, shell=True)
        (out3, err3) = proc3.communicate()
        print "euareinfo output:", out3, "Error" ,err3
        # Test if the email was Not found and if not try admin user email instead
        if "Can not find user" in out3 or not out3:
                print "in Can not find user or string empty - error path trying to get admin users email"
                command4 = "euare-usergetinfo -u admin -k email --delegate=" + AccountName
                proc4 = subprocess.Popen(command4, stdout=subprocess.PIPE, shell=True)
                (out4, err4) = proc4.communicate()
		try:
               		accountEmail = out4.split(None,1)[1]
		except:
			e = sys.exc_info()[0]
               		print "exception occurred: ",e
			accountEmail = "Can not find email for account " + AccountName
                	#No test for situation if admin does not have email either
        else:
                accountEmail = out3.split(None,1)[1]
        return accountEmail

def insertToDb(sampledatetime,AccountId,AccountName,AccountEmail):
        print "insertToDb: inserting Acccount ID",AccountId, "to db - AccountName:", AccountName, " Account Email", AccountEmail
        try:
                cursor.execute("""INSERT INTO "accounthistory" (
                        sampledatetime,
                        AccountId,
                        AccountName,
                        AccountEmail
                        )
                        VALUES (%s,%s,%s,%s);""",(
                        sampledatetime,
                        AccountId,
                        AccountName,
                        AccountEmail
                        )
                )
                #conn execute ends
                conn.commit()
                cleanCloudDataVariables()
                print "insertToDb: inserting account ID",AccountId, "to db - AccountName: AFTER CLEANUP", AccountName, " Account Email", AccountEmail
        except:
                e = sys.exc_info()[0]
                print "exception occurred: ",e
#
#
# Def insertToDb ends
#

def cleanCloudDataVariables():
        print "cleanCloudDataVariables - AcountName:",AccountName," ID", AccountId
        global AccountId
        AccountId = ''
        global AccountName
        AccountName = ''
        global AccountEmail
        AccountEmail = ''
        print "cleanCloudDataVariables - AccountName:",AccountName," ID", AccountId
#
# Def cleanCloudDataVariables ends
#


def AccountNotAlreadyInDb(AccountId):
        #print "AccountNotAlreadyInDb: searching Image:",imageId," from db"
        try:
                cursor.execute("SELECT * from accounthistory WHERE accountid=%(AccountId)s ",{'AccountId': AccountId} )
                print "AccountNotAlreadyInDb:",cursor.statusmessage
                row = cursor.fetchone()
                print "AccountNotAlreadyInDb: Row fetchone()",row
                if row == None:
                        print "AccountNotAlreadyInDb: row == None return 0"
                        return 1
                else:
                        print "AccountNotAlreadyInDb: row != None return 1"
                        return 0
        except Exception, e:
                #e = sys.exc_info()[0]
                print "AccountNotAlreadyInDb: exception occurred: ",e.pgerror
                return 0
#
# is Image In DB def ends
#

# Connect to DB
#

conn_string = 'host=localhost dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd+ ' port=' + dbPort

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

print "\n\nConnected to database", database, "on localhost"

for (event, node) in iterparse(cloudhistoryxmlpath, ['start', 'end']):
        if event == 'end':
                #print "\n End tag", node.tag
                if node.tag == "{http://iam.amazonaws.com/doc/2010-05-08/}member":
                        print "\n\n END member", AccountId, AccountName
                        #print "\nAll End Event: Image data from debug:\n" ,imageId \
                        #       ,imageLocation,imageState \
                        #       ,imageOwnerId,isPublic,architecture \
                        #       ,platform,imageType,name \
                        #       ,description,rootDeviceType,rootDeviceName
                        if AccountNotAlreadyInDb(AccountId):
                                insertToDb(sampledatetime,AccountId \
                                ,AccountName,AccountEmail)
                        #else:
                        #       print "End Event: Image already in imagehistory DB not inserting it again"
                if node.tag == "{http://iam.amazonaws.com/doc/2010-05-08/}AccountName":
                        AccountName = node.text
                        print "\n Account Name:",node.text
                        AccountEmail = getEmail(AccountName)
                        print "\n Account Email:",AccountEmail
                        continue
                if node.tag == "{http://iam.amazonaws.com/doc/2010-05-08/}AccountId":
                        AccountId = node.text
                        print "\n Account Id:",node.text
                        continue

# Close communication with the database
cursor.close()
conn.close()
