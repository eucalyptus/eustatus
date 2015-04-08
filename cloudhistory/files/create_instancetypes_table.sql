CREATE TABLE "instancetypes_history"
(
 instancetype_id serial primary key,
 instancetype VARCHAR(30),
 corecount INTEGER,
 memory_mb INTEGER,
 diskspace_gb INTEGER,
 firstdatetime TIMESTAMP WITH TIME ZONE,
 sampledatetime TIMESTAMP WITH TIME ZONE
);
