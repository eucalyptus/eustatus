#!/usr/bin/python

#
#  Python script to read tidied and stripped xml from euca-describe-instances verbose --debug to postgres DB as an eemon user
#
import os
import sys
import string
import psycopg2
import datetime
import StringIO
from xml.etree.ElementTree import iterparse
import argparse

sampledatetime = datetime.datetime.utcnow()
#print "sampledatetime: ",sampledatetime

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

# Instance data
reservationId = ''
# Owner Account Id
ownerId = ''
#Security Group name
groupName = ''
groupId = ''
instanceId = ''
imageId = ''
# <instanceState><name>
#instanceState = ''
name = ''
privateDnsName = ''
dnsName = ''
#keypair name
keyName = ''
amiLaunchIndex = ''
instanceType = ''
launchTime = ''
#<placement><availabilityZone>
availabilityZone = ''
kernelId = ''
ramdiskId = ''
privateIpAddress = ''
ipAddress = ''
# ebs or normal instance store
rootDeviceType = ''
rootDeviceName = ''
eucanodeip = ''
key = ''
value = ''
virtualizationType = ''

previous_endtag = "{http://ec2.amazonaws.com/doc/2013-02-01/}groupId"
previous_nodetext = "empty"

def insertToDb(rervationId,reservationId,ownerId,groupId,instanceId,imageId,name,privateDnsName,dnsName,keyName,amiLaunchIndex,instanceType,launchTime,availabilityZone,kernelId,ramdiskId,privateIpAddress,ipAddress,groupName,rootDeviceType,rootDeviceName,eucanodeip,virtualizationType):
	print "insertToDb: inserting Instance  ID",instanceId, "to db"
	monitoringstate = ''
	try:
		cursor.execute("INSERT INTO instancehistory (\
			sampledatetime,reservationId	\
			,ownerId,groupId		\
			,instanceId,imageId,name	\
			,privateDnsName,dnsName		\
			,keyName,amiLaunchIndex		\
			,instanceType,launchTime	\
			,availabilityZone,monitoringstate		\
			,kernelId,ramdiskId		\
			,privateIpAddress,ipAddress,groupName	\
			,rootDeviceType,rootDeviceName,eucanodeip,virtualizationType)	\
			VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",( sampledatetime\
			,reservationId,ownerId		\
                        ,groupId,instanceId		\
                        ,imageId,name,privateDnsName	\
                        ,dnsName,keyName		\
                        ,amiLaunchIndex,instanceType	\
                        ,launchTime,availabilityZone,monitoringstate	\
                        ,kernelId,ramdiskId		\
                        ,privateIpAddress,ipAddress,groupName	\
                        ,rootDeviceType,rootDeviceName,eucanodeip,virtualizationType))
		#conn execute ends
		conn.commit()
		#print"\ncursor status ",cursor.statusmessage
		cleanCloudDataVariables()
	except Exception, e:
		#e = sys.exc_info()[0]
		print "exception occurred: ",e.pgerror
#
#
# Def insertToDb ends
# 

def cleanCloudDataVariables():
	#print "cleanCloudDataVariables - :rootDeviceName",rootDeviceName
	global reservationId
	reservationId = ''
	global ownerId
	ownerId = ''
	global groupId
	groupId = ''
	global groupName
	groupName = ''
	global instanceId
	instanceId = ''
	global imageId
	imageId = ''
	global name
	name = ''
	global privateDnsName
	privateDnsName = ''
	global dnsName
	dnsName = ''
	global keyName
	keyName = ''
	global amiLaunchIndex
	amiLaunchIndex = 0
	global instanceType
	instanceType = ''
	global launchTime
	launchTime = ''
	global kernelId
	kernelId = ''
	global ramdiskId
	ramdiskId = ''
	global privateIpAddress
	privateIpAddress = ''
	global ipAddress
	ipAddress = ''
	global rootDeviceType
	rootDeviceType = ''
	global rootDeviceName
	rootDeviceName = ''
	global eucanodeip
	eucanodeip = ''
	global key
	key = ''
	global value
	value = ''
	global virtualizationType
	virtualizationType = ''
	#print "cleanCloudDataVariables - description:",description
#
# Def cleanCloudDataVariables ends
#



def updateTimestamp(instanceId):
	print "updateTimestamp instance ID :",instanceId," with sampledatetime:",sampledatetime
	try:
		cursor.execute("UPDATE instancehistory SET sampledatetime=%s WHERE instanceid=%s",(sampledatetime,instanceId) )
		conn.commit()
	except Exception, e:
		print "exception occurred: ",e.pgerror

#
#  End Update TimeStamp
#

def instanceNotAlreadyInDb(instanceId):
	print "instanceNotAlreadyInDb: searching InstanceId:",instanceId," from db"
	try:
		cursor.execute("SELECT * from instancehistory WHERE instanceid=%(instanceId)s ",{'instanceId': instanceId} )
		print "instanceNotAlreadyInDb:",cursor.statusmessage
		row = cursor.fetchone()
		print "instanceNotAlreadyInDb: Row fetchone()",row
		if row == None:
			print "instanceNotAlreadyInDb: row == None return 0"
			return 1
		else:
			print "instanceNotAlreadyInDb: row != None return 1"
			return 0
	except:
		e = sys.exc_info()[0]
		print "imageNotAlreadyInDb: exception occurred: ",e
		return 0
#
# is Instance In DB def ends
#

# Connect to DB
#

conn_string = 'host=localhost dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd + ' port=' + dbPort
#print conn_string

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

print "\n\nConnected to database", database, "on localhost"

depth = 0

for (event, node) in iterparse(cloudhistoryxmlpath, ['start', 'end']):
	#
	# Start Event in iterparse <some tag>
	if event == 'end':
		print "\n End tag", node.tag, " Previous tag: ",previous_endtag
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}item" and previous_endtag == "{http://ec2.amazonaws.com/doc/2013-02-01/}instancesSet":
			print "\n\n\n\n END instance previous end event tag",previous_endtag
			print "All instance data",reservationId \
				,ownerId,groupId		\
				,instanceId,imageId,name	\
                        	,privateDnsName,dnsName		\
                        	,keyName,amiLaunchIndex,instanceType \
                        	,launchTime, availabilityZone	\
                        	,kernelId,ramdiskId		\
                        	,privateIpAddress,ipAddress,groupName	\
				,rootDeviceType,rootDeviceName,eucanodeip,virtualizationType
			
                        #  if instanceState != running "Not updating the timestamp anymore"
			if name == "running":
				if instanceNotAlreadyInDb(instanceId):
					insertToDb(sampledatetime,reservationId \
						,ownerId,groupId		\
                                		,instanceId,imageId,name	\
                                		,privateDnsName,dnsName		\
                                		,keyName,amiLaunchIndex, instanceType \
                                		,launchTime, availabilityZone	\
                                		,kernelId,ramdiskId		\
                                		,privateIpAddress,ipAddress,groupName	\
                                		,rootDeviceType,rootDeviceName	\
						,eucanodeip,virtualizationType
						)
				else:
					print "End Event: Instance already in DB updateing timestamp"
					updateTimestamp(instanceId)
			else:
				print "instance not in running state not adding to DB"
		if  node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}value" and previous_endtag == "{http://ec2.amazonaws.com/doc/2013-02-01/}key":
                        print "\n END tag value previous end key",previous_endtag
			if previous_nodetext == "euca:node":
				eucanodeip = node.text
				print "\n eucanodeip",eucanodeip

		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}reservationId":
			reservationId = node.text
                        #print "\n reservationId:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}ownerId":
                        ownerId = node.text
                        #print "\n ownerId :",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}groupId":
                        groupId = node.text
                        #print "\n groupId :",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}groupName":
                        groupName = node.text
                        #print "\n groupName :",node.text," depth:",depth
                        previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}instanceId":
                        instanceId = node.text
                        #print "\n instanceId:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}imageId":
                        imageId = node.text
                        #print "\n imageId:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}name":
                        name = node.text
                        print "\n name:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}privateDnsName":
                        privateDnsName = node.text
                        #print "\n privateDnsName:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}dnsName":
                        dnsName = node.text
                        #print "\n dnsName:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}keyName":
                        keyName = node.text
                        #print "\n keyName:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}amiLaunchIndex":
                        amiLaunchIndex = node.text
                        #print "\n amiLaunchIndex:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}instanceType":
                        instanceType = node.text
                        #print "\n instanceType ",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}launchTime":
                        launchTime = node.text
                        #print "\n launchTime:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}availabilityZone":
                        availabilityZone = node.text
                        #print "\n availabilityZone:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}kernelId":
                        kernelId = node.text
                        #print "\n kernelId:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}ramdiskId":
                        ramdiskId = node.text
                        #print "\n ramdiskId:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}privateIpAddress":
                        privateIpAddress = node.text
                        #print "\n privateIpAddress:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}ipAddress":
                        ipAddress = node.text
                        #print "\n ipAddress:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}rootDeviceType":
                        rootDeviceType = node.text
                        #print "\n rootDeviceType:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}rootDeviceName":
                        rootDeviceName = node.text
                        #print "\n rootDeviceName:",node.text," depth:",depth
			previous_endtag = node.tag
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}blockDeviceMapping":
			print "\n blockDeviceMapping:",node.text
                        previous_endtag = node.tag
                        continue
		if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}virtualizationType":
			virtualizationType = node.text
                        print "\n /virtualizationType:",node.text
                        previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}key":
			key = node.text
                        print "\n /key:",node.text
                        previous_endtag = node.tag
			previous_nodetext = node.text
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}value":
                        value = node.text
                        print "\n /value:",node.text
                        previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}iamInstanceProfile":
                        print "\n /iamInstanceProfile:",node.text
                        previous_endtag = node.tag
                        continue
                if node.tag == "{http://ec2.amazonaws.com/doc/2013-02-01/}instancesSet":
                        print "\n /instancesSet:",node.text
                        previous_endtag = node.tag
                        continue

# Close communication with the database
cursor.close()
conn.close()
