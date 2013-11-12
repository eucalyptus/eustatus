CREATE TABLE "cloudstatushistory"
(
sampledatetime timestamp without time zone,
zone varchar(256),
testoutput text,
describeazverbose text,
CONSTRAINT "cloudstatushistory_pkey" PRIMARY KEY (sampledatetime )
);
