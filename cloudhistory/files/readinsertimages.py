#!/usr/bin/python

#
#  Python script to read tidied and stripped xml from euca-describe-images --debug to postgres DB as an user level user
#
import sys
import string
import psycopg2
import datetime
import StringIO
from xml.etree.ElementTree import iterparse
import argparse

sampledatetime = datetime.datetime.now()

#Get database name for postgres connect string from argparse
parser = argparse.ArgumentParser()
parser.add_argument('-n','--databasename')
parser.add_argument('-p','--databasepassword')
parser.add_argument('-port','--databaseport',default ="5432")
parser.add_argument('-u','--databaseusername',default = 'eemon')
parser.add_argument('-x','--pathtotidyxmlfile', required=True)

args = parser.parse_args()
#print "Arguments",args

database=args.databasename
dbPasswd=args.databasepassword
dbPort=args.databaseport
dbUser=args.databaseusername
cloudhistoryxmlpath=args.pathtotidyxmlfile

#print "name pw port user xml",database,dbPasswd,dbPort,dbUser,cloudhistoryxmlpath

xmlschemaversion='2014-06-15'

# Image  EMI id
imageId = 'None'
# Image Location in bukkits
imageLocation = ''
# imageState available deregistered ...
imageState = ''
# Account id ow image owner
imageOwnerId = ''
# isPublic  boolean
isPublic = ''
#architecture
architecture = ''
# Platform
platform = ''
# imageType  kernel ramdisk image
imageType = ''
# name - in euca 3.1.2 same as imageId
name =''
# Description given in register image
description = ''
#rootDeviceType
rootDeviceType =''
rootDeviceName = ''
virtualizationType = ''

def insertToDb(sampledatetime,imageId,imageLocation,imageState,imageOwnerId,isPublic,architecture,platform,imageType,name,description,rootDeviceType,rootDeviceName,virtualizationType):
	if imageId == "None":
		print " not inserting empty imageId",imageId
		return 1

	print "insertToDb: inserting image ID",imageId, "to db at",sampledatetime, " imageLocation:",imageLocation
	try:
		cursor.execute("""INSERT INTO "imagehistory" (
			sampledatetime,
			imageId,
			imageLocation,
			imageState,
			imageOwnerId,
			isPublic,
			architecture,
			platform,
			imageType,
			name,
			description,
			rootDeviceType,
			rootDeviceName,
			virtualizationType
			)	
			VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",(
			sampledatetime,
			imageId,
        		imageLocation,
        		imageState,
        		imageOwnerId,
        		isPublic,
        		architecture,
        		platform,
        		imageType,
			name,
			description,
			rootDeviceType,
			rootDeviceName,
			virtualizationType
			)
		)
		#conn execute ends
		conn.commit()
		cleanCloudDataVariables()
	except:
		e = sys.exc_info()[0]
		print "exception occurred: ",e
#
#
# Def insertToDb ends
# 

def cleanCloudDataVariables():
        #print "cleanCloudDataVariables - description:",description," imageLocation:",imageLocation
        global imageId
        imageId = 'None'
        global imageLocation
        imageLocation = ''
        global imageState
        imageState = ''
        global imageOwnerId
        imageOwnerId = ''
        global isPublic
        isPublic = ''
        global architecture
        architecture = ''
        global platform
        platform = ''
        global imageType
        imageType = ''
        global name
        name = ''
        global description
        description = ''
        global rootDeviceType
        rootDeviceType = ''
        global rootDeviceName
        rootDeviceName = ''
	global virtualizationType
	virtualizationType = ''
        #print "cleanCloudDataVariables - description:",description," imageLocation:",imageLocation
#
# Def cleanCloudDataVariables ends
#



def imageNotAlreadyInDb(imageId):
	try:
		cursor.execute("SELECT * from imagehistory WHERE imageid=%(imageId)s",{'imageId': imageId} )
		row = cursor.fetchone()
		if row == None:
			return 1
		else:
			return 0
	except:
		e = sys.exc_info()[0]
		print "imageNotAlreadyInDb: exception occurred: ",e
		return 0
#
# is Image In DB def ends
#


# Connect to DB
#

conn_string = 'host=localhost dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd + ' port=' + dbPort

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# iterparse using default end event since end,start caused None child elements
context = iterparse(cloudhistoryxmlpath, events=("start", "end"))
root = None

#for (event, node) in iterparse(cloudhistoryxmlpath, ['start', 'end']):
for event, node in context:
	if event == "start" and root is None:
		root = node	# the first element is root
        if event == 'end':
                #print "\n End tag", node.tag
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}item":
			if imageNotAlreadyInDb(imageId):
				insertToDb(sampledatetime,imageId \
				,imageLocation,imageState \
				,imageOwnerId,isPublic,architecture \
				,platform,imageType,name,description \
				,rootDeviceType,rootDeviceName,virtualizationType)
			else:
				#print "End Event: Image already in imagehistory DB not inserting it again"
				cleanCloudDataVariables()
				#print "End Tag Clearing root and node at item end"
				node.clear()
				root.clear()
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}imageId":
                        imageId = node.text
                        #print "\n imageId:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}imageLocation":
                        imageLocation = node.text
                        #print "\n imageLocation:",node.text," Node tag",node.tag
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}imageState":
                        imageState = node.text
                        #print "\n imageState:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}imageOwnerId":
                        imageOwnerId = node.text
                        #print "\n imageOwnerId:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}isPublic":
                        isPublic = node.text
                        #print "\n isPublic:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}architecture":
                        architecture = node.text
                        #print "\n architecture:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}platform":
                        platform = node.text
                        #print "\n platform ",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}imageType":
                        imageType = node.text
                        #print "\n imageType:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}name":
                        name = node.text
                        #print "\n name:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}description":
                        description = node.text
                        #print "\n description:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}rootDeviceType":
                        rootDeviceType = node.text
                        #print "\n rootDeviceType:",node.text
                        node.clear()
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}rootDeviceName":
                        rootDeviceName = node.text
                        #print "\n rootDeviceName:",node.text
                        node.clear()
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}virtualizationType":
                        virtualizationType = node.text
                        print "\n virtualizationType:",node.text
                        node.clear()
                        continue
# Close communication with the database
cursor.close()
conn.close()
