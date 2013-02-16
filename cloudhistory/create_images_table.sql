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
CREATE TABLE "imagehistory"
(
sampledatetime timestamp without time zone,
imageid varchar(255) NOT NULL,
imagelocation varchar(255),
imagestate varchar(255),
imageownerId varchar(255),
ispublic varchar(255),
architecture varchar(255),
platform varchar(255),
imagetype varchar(255),
name varchar(255),
description varchar(255),
rootdevicetype varchar(255),
rootdevicename  varchar(255),
CONSTRAINT "imagehistory_pkey" PRIMARY KEY (imageId )
);
