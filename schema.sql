CREATE SEQUENCE users_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

CREATE TABLE "users" (
"id" int4 NOT NULL DEFAULT nextval('users_id_seq'::regclass),
"password" varchar(32) COLLATE "default",
"nick_name" varchar(128) COLLATE "default" NOT NULL,
"creation_time" timestamp(6),
"login_time" timestamp(6),
"is_active" bool NOT NULL DEFAULT false,
CONSTRAINT "users_pkey" PRIMARY KEY ("id")
)
WITHOUT OIDS;