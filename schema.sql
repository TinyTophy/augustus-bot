-- DROP TABLE IF EXISTS Guild_Prefix;
-- DROP TABLE IF EXISTS 
-- DROP TABLE IF EXISTS Guild;
-- DROP TABLE IF EXISTS Prefix;


CREATE TABLE IF NOT EXISTS Guild (
	id BIGINT PRIMARY KEY,
	muterole_id	INTEGER,
	modrole_id INTEGER,
	log_id INTEGER,
	modlog_id INTEGER,
	modmail_id INTEGER,
	verify_role_id INTEGER,
	verify_log_id INTEGER,
	autoclose BOOLEAN
);
CREATE TABLE IF NOT EXISTS Prefix (
	id SERIAL PRIMARY KEY,
	prefix VARCHAR(5)
);
CREATE TABLE IF NOT EXISTS Guild_Prefix (
	id SERIAL PRIMARY KEY,
	prefix_id INTEGER NOT NULL,
	guild_id BIGINT NOT NULL,
	FOREIGN KEY(prefix_id) REFERENCES Prefix(id),
	FOREIGN KEY(guild_id) REFERENCES Guild(id)
);
CREATE TABLE IF NOT EXISTS Discord_User (
	id BIGINT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS Member (
	id SERIAL PRIMARY KEY,
	guild_id BIGINT NOT NULL,
	member_id BIGINT NOT NULL,
	FOREIGN KEY(guild_id) REFERENCES Guild(id),
	FOREIGN KEY(member_id) REFERENCES Discord_User(id)
);
CREATE TABLE IF NOT EXISTS Discord_Role (
	role_id	BIGINT PRIMARY KEY,
	guild_id BIGINT NOT NULL,
	FOREIGN KEY(guild_id) REFERENCES Guild(id)
);
-- CREATE TABLE IF NOT EXISTS Member_Role (
-- 	id SERIAL PRIMARY KEY,
-- 	role_id INTEGER NOT NULL,
-- 	member_id INTEGER NOT NULL,
-- 	FOREIGN KEY(role_id) REFERENCES Discord_Role(role_id),
-- 	FOREIGN KEY(member_id) REFERENCES Member(id)
-- );

-- CREATE TABLE IF NOT EXISTS Modlog_Entry (
-- 	id SERIAL PRIMARY KEY,
-- 	case_id INTEGER NOT NULL,
-- 	guild_id INTEGER NOT NULL,
-- 	modlog_id INTEGER NOT NULL,
-- 	mod_type VARCHAR NOT NULL,
-- 	offender_id INTEGER NOT NULL,
-- 	reason VARCHAR NOT NULL,
-- 	mod_id INTEGER NOT NULL,
-- 	message_id INTEGER,
-- 	FOREIGN KEY(guild_id) REFERENCES Guild(id)
-- );
-- CREATE TABLE IF NOT EXISTS Reaction_Role (
-- 	id SERIAL PRIMARY KEY,
-- 	guild_id INTEGER NOT NULL,
-- 	role_id INTEGER NOT NULL UNIQUE,
-- 	message_id INTEGER NOT NULL,
-- 	reaction VARCHAR NOT NULL,
-- 	status VARCHAR,
-- 	FOREIGN KEY(role_id) REFERENCES Discord_Role(role_id),
-- 	FOREIGN KEY(guild_id) REFERENCES Guild(id)
-- );
-- CREATE TABLE IF NOT EXISTS Vote (
-- 	id SERIAL PRIMARY KEY,
-- 	guild_id INTEGER NOT NULL,
-- 	vote_start TIMESTAMP,
-- 	vote_end TIMESTAMP,
-- 	vote_msg VARCHAR NOT NULL,
-- 	FOREIGN KEY(guild_id) REFERENCES Guild(id)
-- );
