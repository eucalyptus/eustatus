/*
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
*/
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
