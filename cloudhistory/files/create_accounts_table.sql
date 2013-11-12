CREATE TABLE "accounthistory"
(
sampledatetime timestamp without time zone,
AccountId varchar(255) NOT NULL,
AccountName varchar(255),
AccountEmail varchar(255),
CONSTRAINT "accounthistory_pkey" PRIMARY KEY (AccountId )
);
