CREATE TABLE "iphistory"
(
sampledatetime timestamp without time zone,
firstdatetime timestamp without time zone,
publicIp varchar(255) NOT NULL,
instanceId varchar(255),
username varchar(255),
hash varchar(255),
CONSTRAINT "iphistory_pkey" PRIMARY KEY (hash )
);
