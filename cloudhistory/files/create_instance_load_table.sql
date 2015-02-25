CREATE TABLE "instanceloadhistory"
(
sampledatetime timestamp without time zone NOT NULL,
instanceid varchar(255) NOT NULL,
cpuloadpercent double precision,
readrequests double precision,
writerequests double precision,
netrxbytes double precision,
nettxbytes double precision,
CONSTRAINT "instanceloadhistory_pkey" PRIMARY KEY (sampledatetime,instanceid )
);
