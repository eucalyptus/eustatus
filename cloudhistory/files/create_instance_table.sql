CREATE TABLE "instancehistory"
(
sampledatetime timestamp without time zone,
reservationid varchar(255),
ownerId varchar(255),
groupId varchar(255),
instanceId varchar(255) NOT NULL,
imageId varchar(255),
name varchar(255),
privateDnsName varchar(255),
dnsName varchar(255),
keyName varchar(255),
amiLaunchIndex integer,
instanceType varchar(255),
launchTime timestamp without time zone,
availabilityzone varchar(255),
kernelId varchar(255),
ramdiskId varchar(255),
privateIpAddress varchar(255),
ipAddress varchar(255),
rootDeviceType varchar(255),
rootDeviceName varchar(255),
CONSTRAINT "instancehistory_pkey" PRIMARY KEY (instanceId )
);
