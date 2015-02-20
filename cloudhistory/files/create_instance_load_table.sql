CREATE TABLE "instanceloadhistory"
(
sampledatetime timestamp without time zone NOT NULL,
instanceid	varchar(255) NOT NULL,
cpuloadpercent		double precision,
iopsload		double precision,
nettxbytes		double precision,
netrxbytes		double precision,
mem			double precision,
CONSTRAINT "instanceloadhistory_pkey" PRIMARY KEY (sampledatetime,instanceid )
);
