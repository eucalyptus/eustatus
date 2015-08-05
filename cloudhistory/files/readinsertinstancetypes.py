#!/usr/bin/python
from xml.etree.ElementTree import iterparse
import psycopg2
import psycopg2.extras
import sys, traceback
from datetime import datetime
import argparse

# python script to insert samples of instancetypes
# euca-describe-instance-types --debug 2> instancetypes.xml
# tidy -xml -i -q  -w 0 -o tidy_instancetypes.xml < instancetypes.xml

# Node tags in instancetypes XML
#xmlschemaversion='2013-02-01'
xmlschemaversion='2014-06-15'
INSTANCE_TYPE_NAME= "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}name"
INSTANCE_TYPE_CPU= "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}cpu"
INSTANCE_TYPE_MEMORY= "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}memory"
INSTANCE_TYPE_DISK= "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}disk"
#Not used currently
INSTANCE_TYPE_AVAILABILITY=  "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}availability"
#Not used currently
INSTANCE_TYPE_EPHEMERALDISK= "{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}ephemeralDisk"

## Database args
dbhost="127.0.0.1"
database="postgres"
dbUser=""
dbPasswd=""
dbPort=""

instanceTypesInDB ={}
instanceTypesInXml = {}
sample_executiontime = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument('-n','--databasename')
parser.add_argument('-p','--databasepassword')
parser.add_argument('-port','--databaseport',default ='5432')
parser.add_argument('-u','--databaseusername',default = 'eemon')
parser.add_argument('-x','--pathtotidyxmlfile', required=True)

args = parser.parse_args()
database=args.databasename
dbPasswd=args.databasepassword
dbPort=args.databaseport
dbUser=args.databaseusername
cloudhistoryxmlpath=args.pathtotidyxmlfile

""" a sample of InstanceType in a specific time """
class InstanceTypeSample:
	def __init__(self,instancetype,corecount,memory_mb,diskspace_gb,instancetype_id=None):
		self.instancetype_id = instancetype_id;
		self.instancetype = instancetype;
		self.corecount = corecount;
		self.memory_mb = memory_mb;
		self.diskspace_gb = diskspace_gb;

        def __eq__(self,other):
                return (isinstance(other,self.__class__)
                and self.instancetype == other.instancetype and self.corecount == other.corecount
                and self.memory_mb == other.memory_mb and self.diskspace_gb == other.diskspace_gb)

        def __ne__(self,other):
                return not self.__eq__(other)

        def __repr__(self):
                return str(self.__dict__)
	
def processFromXml(rawXml):
		instancetype=''
		corecount=''
		memory_mb=''
		diskspace_gb =''
		for (event, node) in iterparse(rawXml,events=("start","end")):
			if event == "end":
				if node.tag == INSTANCE_TYPE_CPU:
					corecount = int(node.text)
				if node.tag == INSTANCE_TYPE_DISK:
					diskspace_gb = int(node.text)
				if node.tag == INSTANCE_TYPE_MEMORY:
					memory_mb = int(node.text)
				if node.tag == INSTANCE_TYPE_NAME:
					instancetype = node.text
				if node.tag =="{http://ec2.amazonaws.com/doc/"+xmlschemaversion+"/}item":
					its = InstanceTypeSample(instancetype,corecount,memory_mb,diskspace_gb)
					instanceTypesInXml[its.instancetype] = its
					instancetype=''
					corecount=''
					memory_mb=''
					diskspace_gb =''

def getPGConnection():
	conn_string = 'host='+dbhost+' dbname=' + database + ' user=' + dbUser+ ' password=' + dbPasswd+ ' port=' + dbPort
	conn = psycopg2.connect(conn_string)
	return conn

def getLatestInstanceTypesFromDB():
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	try: 
		cursor.execute("""select 
			it.instancetype_id, it.instancetype, it.corecount, it.memory_mb, it.diskspace_gb 
			 from
			  public.instancetypes_history it,
			  (SELECT instancetype, max(sampledatetime)as sampledatetime from public.instancetypes_history group by instancetype)it2 
			  where  it.sampledatetime = it2.sampledatetime AND it.instancetype=it2.instancetype;""")
		for rec in cursor.fetchall():
			thisSample = InstanceTypeSample(rec['instancetype'],rec['corecount'],rec['memory_mb'],rec['diskspace_gb'],rec['instancetype_id'])
			instanceTypesInDB[thisSample.instancetype] = thisSample
	except:
		e = sys.exc_info()
		print "exception when reading: ",e
	
def updateInstanceTypeToDB(instanceTypeSample):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
	try:
		cursor.execute("""UPDATE "instancetypes_history" 
		   SET sampledatetime = %s where instancetype_id = %s;""",(
		   sample_executiontime,instanceTypeSample.instancetype_id)
		   )
		connection.commit()
	except:
		e = sys.exc_info()
		print "exception when updating: ",e

def insertInstanceTypeToDB(instanceTypeSample):
	cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:		
			
                cursor.execute("""INSERT INTO "instancetypes_history" (
                        instancetype,
                        corecount,
                        memory_mb,
                        diskspace_gb,
                        firstdatetime,
                        sampledatetime
                        )
                        VALUES (%s,%s,%s,%s,%s,%s);""",(
                        instanceTypeSample.instancetype,
                        instanceTypeSample.corecount	,
                        instanceTypeSample.memory_mb,
                        instanceTypeSample.diskspace_gb,
                        sample_executiontime,
                        sample_executiontime                        
                        )
                )
                connection.commit()
        except:
                e = sys.exc_info()
                print "exception when inserting: ",e


connection = getPGConnection()
# read the latest data DB contains to InstanceTypesInDB
getLatestInstanceTypesFromDB()
# parse xml data to instanceTypesInXml
processFromXml(cloudhistoryxmlpath)

#iterate over types found in XML:
# - insert if type has changed or doesn't yet exist
# - update only timestamp if type exists and properties aren't changed
for instanceTypeName in instanceTypesInXml:
	if instanceTypeName in instanceTypesInDB:
		if instanceTypesInDB[instanceTypeName] == instanceTypesInXml[instanceTypeName]:
			updateInstanceTypeToDB(instanceTypesInDB[instanceTypeName])
		else:
			insertInstanceTypeToDB(instanceTypesInXml[instanceTypeName])
	else:
		insertInstanceTypeToDB(instanceTypesInXml[instanceTypeName])
