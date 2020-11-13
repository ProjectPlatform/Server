BEGIN TRANSACTION;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS education_records CASCADE;
DROP TABLE IF EXISTS career_records CASCADE;
DROP TABLE IF EXISTS additional_experience_records CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS user_tags CASCADE;
DROP TABLE IF EXISTS connections CASCADE;
DROP TABLE IF EXISTS images CASCADE;
DROP TYPE IF EXISTS education_level;
CREATE TYPE education_level AS enum (
    'enrollee',
    'undergraduate',
    'graduate',
    'postgraduate'
);
CREATE TABLE images (
    id varchar(12) PRIMARY KEY,
    image_path varchar(256),
    thumbnail_path varchar(256)
);
CREATE TABLE documents (
    id varchar(12) PRIMARY KEY,
    name varchar(256) NOT NULL;
path varchar(256 NOT NULL),
);
CREATE TABLE users (
    id varchar(12) PRIMARY KEY,
    nick varchar(64) UNIQUE NOT NULL,
    password varchar(128) NOT NULL,
    name varchar(128) NOT NULL,
    email varchar(128) UNIQUE NOT NULL,
    avatar_id varchar(12) REFERENCES images ON DELETE SET NULL,
    pspicture jsonb
);
CREATE TABLE education_records (
    id varchar(12) PRIMARY KEY,
    user_id varchar(12) REFERENCES users ON DELETE CASCADE NOT NULL,
    level education_level NOT NULL,
    institution varchar(256) NOT NULL,
    from_year integer NOT NULL CHECK (from_year > 0),
    to_year integer CHECK (to_year IS NULL OR to_year > 0),
    CHECK (to_year IS NULL OR to_year >= from_year)
);
CREATE TABLE career_records (
    id varchar(12) PRIMARY KEY,
    user_id varchar(12) REFERENCES users ON DELETE CASCADE NOT NULL,
    company varchar(256) NOT NULL,
    position varchar(256) NOT NULL,
    from_year integer NOT NULL CHECK (from_year > 0),
    to_year integer CHECK (to_year IS NULL OR to_year > 0),
    CHECK (to_year IS NULL OR to_year >= from_year)
);
CREATE TABLE additional_experience_records (
    id varchar(12) PRIMARY KEY,
    user_id varchar(12) REFERENCES users ON DELETE CASCADE NOT NULL,
    description text NOT NULL
);
CREATE TABLE tags (
    id varchar(12) PRIMARY KEY,
    name varchar(64) NOT NULL,
    hierarchy ltree NOT NULL
);
CREATE TABLE user_tags (
    id varchar(12) PRIMARY KEY,
    user_id varchar(12) REFERENCES users ON DELETE CASCADE NOT NULL,
    tag_id varchar(12) REFERENCES tags ON DELETE CASCADE NOT NULL
);
CREATE TABLE connections (
    id varchar(12) PRIMARY KEY,
    from_user_id varchar(12) REFERENCES users ON DELETE CASCADE NOT NULL,
    to_user_id varchar(12) REFERENCES users ON DELETE CASCADE NOT NULL,
    groups integer
);
CREATE TABLE chats (
    id varchar(12) PRIMARY KEY,
    name varchar(64) NOT NULL,
    avatar_id varchar(12) REFERENCES images,
    colour integer,
    is_encrypted boolean NOT NULL,
    is_personal boolean NOT NULL,
    is_user_expandable boolean NOT NULL,
    is_user_expandable_modified_by varchar(12) REFERENCES users ON DELETE SET NULL,
    is_non_admin boolean NOT NULL,
    is_non_admin_modified_by varchar(12) REFERENCES users ON DELETE SET NULL,
    non_removable_messages boolean NOT NULL,
    non_removable_messages_modified_by varchar(12) REFERENCES users ON DELETE SET NULL,
    non_modifiable_messages boolean NOT NULL,
    non_modifiable_messages_modified_by varchar(12) REFERENCES users ON DELETE SET NULL,
    auto_remove_messages boolean NOT NULL,
    auto_remove_messages_modified_by varchar(12) REFERENCES users ON DELETE SET NULL,
    auto_remove_period integer CHECK (auto_remove_period IS NULL OR auto_remove_period > 0),
    digest_messages boolean NOT NULL,
    digest_messages_modified_by varchar(12) REFERENCES users ON DELETE SET NULL
);
CREATE TABLE chat_memberships (
    id varchar(12) PRIMARY KEY,
    user_id varchar(12) REFERENCES users NOT NULL ON DELETE CASCADE,
    chat_id varchar(12) REFERENCES chats NOT NULL ON DELETE CASCADE,
    is_admin boolean NOT NULL
);
CREATE TABLE messages (
    id varchar(12) PRIMARY KEY,
    chat_id varchar(12) REFERENCES chats NOT NULL ON DELETE CASCADE,
    time timestamp NOT NULL,
    author_id varchar(12) REFERENCES users ON DELETE SET NULL,
    body text NOT NULL
);
CREATE TABLE message_tags (
    id varchar(12),
    message_id varchar(12) REFERENCES messages NOT NULL ON DELETE CASCADE,
    tag varchar(64) NOT NULL
);
CREATE TABLE message_attachments (
    id varchar(12) PRIMARY KEY,
    document_id varchar(12) REFERENCES documents ON DELETE CASCADE,
    image_id varchar(12) REFERENCES images ON DELETE CASCADE,
    CHECK((document_id IS NULL AND image_id IS NOT NULL) OR (document_id IS NOT NULL AND image_id IS NULL))
);
COMMIT;

