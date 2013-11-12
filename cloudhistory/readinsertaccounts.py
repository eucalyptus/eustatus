#!/usr/bin/python
#
#  Python script to read tidied and stripped xml from
#  euare-accountlist --debug to postgres DB as an histuser user
#
#  Copyright 2013 Nokia Siemens Networks, Authored by Teemu Jalonen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import sys
import string
import psycopg2
import datetime
import StringIO
from xml.etree.ElementTree import iterparse
import argparse

sampledatetime = datetime.datetime.now()
#print "sampledatetime: ",sampledatetime

parser = argparse.ArgumentParser()
parser.add_argument('-n','--databasename')
parser.add_argument('-p','--databasepassword')
parser.add_argument('-port','--databaseport',default ="5432")
parser.add_argument('-u','--databaseusername',default = 'histuser')
parser.add_argument('-x','--pathtotidyxmlfile', required=True)

args = parser.parse_args()

#print "Arguments",args

database=args.databasename
dbPasswd=args.databasepassword
dbPort=args.databaseport
dbUser=args.databaseusername
cloudhistoryxmlpath=args.pathtotidyxmlfile

#print "name pw port user xml",database,dbPasswd,dbPort,dbUser,cloudhistoryxmlpath

# account id
AccountId = ''
# Image Location in bukkits
AccountName = ''


#
# Insert data parsed from xml to database
#
def insertToDb(sampledatetime,AccountId,AccountName):
	print "insertToDb: inserting Acccount ID",AccountId, "to db - AccountName:", AccountName
	try:
		cursor.execute("""INSERT INTO "accounthistory" (
			sampledatetime,
			AccountId,
			AccountName
			)	
			VALUES (%s,%s,%s);""",(
			sampledatetime,
			AccountId,
        		AccountName
			)
		)
		#conn execute ends
		conn.commit()
		cleanCloudDataVariables()
		print "insertToDb: inserting account ID",AccountId, "to db - AccountName: AFTER CLEANUP", AccountName
	except:
		e = sys.exc_info()[0]
		print "exception occurred: ",e
#
#
# Def insertToDb ends
# 


#
# Clean the data from previous account that was inserted to db
#
def cleanCloudDataVariables():
	print "cleanCloudDataVariables - AcountName:",AccountName," ID", AccountId
	global AccountId
	AccountId = ''
	global AccountName
	AccountName = ''
	print "cleanCloudDataVariables - AccountName:",AccountName," ID", AccountId
#
# Def cleanCloudDataVariables ends
#


#
# Check if account is not in DataBAse already
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
conn_string = 'host=localhost dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd+ ' port=' + dbPort

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

#print "\n\nConnected to database", database, "on localhost"


#
#  Main iterparse loop  checking the end event
#
for (event, node) in iterparse(cloudhistoryxmlpath, ['start', 'end']):
        if event == 'end':
                #print "\n End tag", node.tag
                if node.tag == "{http://iam.amazonaws.com/doc/2010-05-08/}member":
                        print "\n\n END member", AccountId, AccountName
                        #print "\nAll End Event: Image data from debug:\n" ,imageId \
                        #	,imageLocation,imageState \
                        #	,imageOwnerId,isPublic,architecture \
                        #	,platform,imageType,name \
                        #	,description,rootDeviceType,rootDeviceName
			if AccountNotAlreadyInDb(AccountId):
				insertToDb(sampledatetime,AccountId \
				,AccountName)
			#else:
			#	print "End Event: Image already in imagehistory DB not inserting it again"
                if node.tag == "{http://iam.amazonaws.com/doc/2010-05-08/}AccountName":
                       	AccountName = node.text
                       	print "\n Account Name:",node.text
                       	continue
                if node.tag == "{http://iam.amazonaws.com/doc/2010-05-08/}AccountId":
                        AccountId = node.text
                        print "\n Account Id:",node.text
                        continue

# Close communication with the database
cursor.close()
conn.close()
