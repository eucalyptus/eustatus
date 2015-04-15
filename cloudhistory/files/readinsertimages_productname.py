#!/usr/bin/python
#
#  Python script to find out the productname using virt-inspector and put it to postgres DB
#  Prerequisites passwordless ssh access to the nodes where instances are running 
#

import sys
import os
import string
import psycopg2
import datetime
import argparse
import paramiko

sampledatetime = datetime.datetime.now()

#Get database name for postgres connect string from argparse
parser = argparse.ArgumentParser()
parser.add_argument('-dh','--databasehostname')
parser.add_argument('-n','--databasename')
parser.add_argument('-p','--databasepassword')
parser.add_argument('-port','--databaseport',default ="5432")
parser.add_argument('-u','--databaseusername',default = 'eemon')

args = parser.parse_args()
#print "Arguments",args

dbHost=args.databasehostname
database=args.databasename
dbPasswd=args.databasepassword
dbPort=args.databaseport
dbUser=args.databaseusername


# Image  EMI id
imageId = 'None'
# productname
ProductName =''

def insertToDb(ImageId,ProductName):
	if imageId == "None":
		print "insertToDb: can not inserting empty imageId:",imageId," ProductName:",ProductName
		return 1

	print "insertToDb: inserting image ID:",imageId, " ProductName:",ProductName
	try:
		cursor.execute("UPDATE imagehistory SET productname=%s WHERE  imageid=%s", (ProductName,ImageId))
		#conn execute ends
		conn.commit()
		cleanCloudDataVariables()
	except:
		e = sys.exc_info()[0]
		print "insertToDb: exception occurred: ",e
#
#
# Def insertToDb ends
# 

def cleanCloudDataVariables():
        #print "CleanCloudDataVariables"
        global imageId
        imageId = 'None'
        global ProductName
        ProductName = ''
        #print "CleanCloudDataVariables:"
#
# Def cleanCloudDataVariables ends
#

def getEmiIds():
	try:
                cursor.execute("SELECT imageid from imagehistory")
		emiIds = cursor.fetchall() 
		return emiIds
        except:
                e = sys.exc_info()[0]
                print "getEmiIds: exception occurred: ",e
                return 0


def imageHasProductName(imageId):
	try:
		cursor.execute("SELECT productname from imagehistory WHERE imageid=%(imageId)s",{'imageId': imageId} )
		row = cursor.fetchone()[0]
		if row == None:
			print "imageHasProductName: No ProductName imageId:",imageId," row:",row
			return 0
		else:
			print "imageHasProductName: ProductName Found !! for imageId:",imageId," row:",row
			return 1
	except:
		e = sys.exc_info()[0]
		print "imageHasProductName: exception occurred: ",e
		return 0
#
# is Image had ProductName def ends
#

def findRunningEmi(imageId):
	try:
               	cursor.execute("select imageid,eucanodeip,instanceid from instancehistory where instancehistory.imageid = %(imageId)s and instancehistory.sampledatetime BETWEEN ( timezone('UTC',now() ) - '10 minutes '::interval)::timestamp AND timezone('UTC', now() ) limit 1",{'imageId': imageId} )
               	row = cursor.fetchone()
                if row == None:
                        print "findRunningEmi: NO runing instance for imageId:",imageId," row:",row ," Found"
                        return 0
                else:
                        print "findRunningEmi: running instance for imageId:",imageId," FOUND row:",row
                        return row
        except:
                e = sys.exc_info()[0]
                print "findRunningEmi: exception occurred: ",e
                return 0

#
# def findRunningEmi def ends
#

def getProductNameFromInstance(instanceId,nodeIp):

	try:
		#virtinspector2cmd = "uptime"
		#virtinspector2cmd = "timeout 50 ssh -oStrictHostKeyChecking=no " + nodeIp + " \'" +"virt-inspector --xml "+instanceId +" 2>/dev/null | virt-inspector2 --xpath \"string(//operatingsystem/product_name)\"" + "\'"
		virtinspector2cmd = "virt-inspector --xml "+instanceId +" 2>/dev/null | virt-inspector2 --xpath \"string(//operatingsystem/product_name)\""
		print "getProductNameFromInstance : ",virtinspector2cmd
		#FIX needed: ubuntu images do not have product_name, they will show as empty space in db
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(nodeIp,username='root')
		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(virtinspector2cmd)
		ProductName = ssh_stdout.readline()
		ssh.close() 
		print "getProductNameFromInstance: ProductName: ", ProductName
		return ProductName
	except:
                e = sys.exc_info()[0]
                print "getProductNameFromInstance: exception occurred: ",e
                return 0


#
# getProductNameFromInstance def ends
#


# 
# Main section
#

try:
	conn_string = 'host=' + dbHost + ' dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd + ' port=' + dbPort
	#print "main: conn string:",conn_string
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()

	rows = getEmiIds()
	if rows !=0:
		print "main: found emi:s"
		for i in rows:
			print "row: ",i[0]
			imageId = i[0]

			#imageId = "emi-11111111"
			print "Main: getting product name"

			if imageHasProductName(imageId):
				print "main: image has already a productname - imageId:",imageId
			else:
				print "main: image does not have a productname - imageId:",imageId
				#
				# try to search the instancehistory if cloud has an instance running with this emi-id
				emiLocationDict = findRunningEmi(imageId)
				print "emilocation: ",emiLocationDict
				if emiLocationDict != 0:
					#
					# get the product name using virt-inspector from running instance
					ProductName = getProductNameFromInstance(emiLocationDict[2],emiLocationDict[1])
					print "Productname:",ProductName
					#
					# insert the product name into DB
					insertToDb(imageId,ProductName)
				else:
					print "main: No running image found"
	else:
		print "main: Did not found emi:s"

except psycopg2.DatabaseError, e:
	print 'main: Error %s' % e

# Close communication with the database
cursor.close()
conn.close()
