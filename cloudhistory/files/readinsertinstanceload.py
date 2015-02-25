#!/usr/bin/python
#
#  Python script to read  xml data of instance load to postgres DB as an eemon user
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


parser = argparse.ArgumentParser()
parser.add_argument('-n','--databasename')
parser.add_argument('-p','--databasepassword')
parser.add_argument('-port','--databaseport',default ="5432")
parser.add_argument('-u','--databaseusername',default = 'eemon')
parser.add_argument('-x','--pathtoxmlfile', required=True)

args = parser.parse_args()

database=args.databasename
dbPasswd=args.databasepassword
dbPort=args.databaseport
dbUser=args.databaseusername
cloudhistoryxmlpath=args.pathtoxmlfile

print "name pw port user xml",database,dbPasswd,dbPort,dbUser,cloudhistoryxmlpath

# sampledatetime  of time when virt-top was sampled
sampledatetime = ''
# eucalyptus Instance Id
InstanceId = ''
# CpuLoad persentage of instance from virt top
CpuLoad = ''
# block read requests
ReadRequests = ''
# block write requests
WriteRequests = ''
# net read bytes
NetRxBytes = ''
# net read bytes
NetTxBytes = ''


def insertToDb(sampledatetime,InstanceId,CpuLoad,ReadRequests,WriteRequests,NetRxBytes,NetTxBytes):
        print "insertToDb: inserting sampletime", sampledatetime, " InstanceId:", InstanceId," CpuLoad:",CpuLoad," ReadRequests:",ReadRequests," WriteRequests:",WriteRequests," NetRxBytes:",NetRxBytes," NetTxBytes:",NetTxBytes
        try:
                cursor.execute("""INSERT INTO "instanceloadhistory" (
                        sampledatetime,
                        instanceid,
                        cpuloadpercent,
			readrequests,
                        writerequests,
			netrxbytes,
			nettxbytes
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s);""",(
                        sampledatetime,
                        InstanceId,
                        CpuLoad,
			ReadRequests,
                        WriteRequests,
			NetRxBytes,
			NetTxBytes
                        )
                )
                #conn execute ends
		print "insertToDb: after cur execute "
                conn.commit()
		print "insertToDb: after comit"
                cleanCloudDataVariables()
		print "insertToDb: after clean sampletime", sampledatetime, " InstanceId:", InstanceId," CpuLoad:",CpuLoad," ReadRequests:",ReadRequests," WriteRequests:",WriteRequests," NetRxBytes:",NetRxBytes," NetTxBytes:",NetTxBytes
	except psycopg2.Error as e:
        	print "\n\n\nUnable to execute,commit!\n"
        	print e.pgerror
		print "insertToDb: doing roll back so we can use the conection for next item\n\n"
		conn.rollback()
#
# Def insertToDb ends
#


def cleanCloudDataVariables():
        print "cleanCloudDataVariables sampledatetime",sampledatetime," InstanceId:",InstanceId," CpuLoad:",CpuLoad," ReadRequests:",ReadRequests," WriteRequests:",WriteRequests," NetRxBytes:",NetRxBytes," NetTxBytes:",NetTxBytes

        global InstanceId
        InstanceId = ''
        global CpuLoad
        CpuLoad = ''
	global sampledatetime
	sampledatetime = ''
        global ReadRequests
        ReadRequests = ''
        global WriteRequests
        WriteRequests = ''
	global NetRxBytes
	NetRxBytes = ''
        global NetTxBytes
	NetTxBytes = ''

	print "cleanCloudDataVariables: after cleanup - sampledatetime",sampledatetime," InstanceId:",InstanceId," CpuLoad:",CpuLoad," ReadRequests:",ReadRequests," WriteRequests:",WriteRequests," NetRxBytes:",NetRxBytes," NetTxBytes:",NetTxBytes
#
# Def cleanCloudDataVariables ends
#

#
# simple test if the value is float
# 12334  and 12.11  is true
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
#
# def isfloat ends
#


# Main loop
# Connect to DB
#

conn_string = 'host=localhost dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd+ ' port=' + dbPort

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

print "\n\nread insert instance load Connected to database", database, "on localhost"

for (event, node) in iterparse(cloudhistoryxmlpath, ['start', 'end']):
	if event == 'end':
		print "   End tag", node.tag
		if node.tag == "item":
			print "END member item inserted into db at end tag :" , node.tag
			print "MAIN: inserting sampledatetime", sampledatetime, " InstanceId:", InstanceId," CpuLoad:",CpuLoad," ReadRequests:",ReadRequests," WriteRequests:",WriteRequests," NetRxBytes:",NetRxBytes," NetTxBytes:",NetTxBytes
			insertToDb(sampledatetime,InstanceId,CpuLoad,ReadRequests,WriteRequests,NetRxBytes,NetTxBytes)
		if node.tag == "InstanceId":
			InstanceId = node.text
			print "\n\n\n    InstanceId:",node.text
			continue
                if node.tag == "Time":
			sampledatetime = node.text
			print "Time:",node.text
			continue
		if node.tag == "CpuLoad":
			if isfloat(node.text):
                        	CpuLoad = node.text
                        	print "CpuLoad:",node.text
			else:
				print "\n\nMain: ERROR cpu value NOT Float - CpuLoad:",node.text
			continue
		if node.tag == "ReadRequests":
			if isfloat(node.text):
                        	ReadRequests = node.text
                        	print "ReadRequests:",node.text
			else:
				print "\n\nMain: ERROR value NOT Float ReadRequests:",node.text
			continue
                if node.tag == "WriteRequests":
			if isfloat(node.text):
                        	WriteRequests = node.text
                        	print "WriteRequests:",node.text
			else:
				print "\n\nMain: ERROR value NOT Float WriteRequests:",node.text
			continue
                if node.tag == "NetRxBytes":
			if isfloat(node.text):
                        	NetRxBytes = node.text
                        	print "NetRxBytes:",node.text
			else:
				print "\n\nMain: ERROR value NOT Float NetRxBytes:",node.text
			continue
		if node.tag == "NetTxBytes":
			if isfloat(node.text):
				NetTxBytes = node.text
				print "NetTxBytes:",node.text
			else:
				print "\n\nMain: ERROR value NOT Float NetTxBytes:",node.text
			continue


# Close communication with the database
cursor.close()
conn.close()
