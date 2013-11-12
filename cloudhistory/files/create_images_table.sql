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
