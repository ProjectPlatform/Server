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
CREATE TABLE users (
    id varchar(12) PRIMARY KEY,
    nick varchar(64) UNIQUE NOT NULL,
    name varchar(128) NOT NULL,
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
COMMIT;

