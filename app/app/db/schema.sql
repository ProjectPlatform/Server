------------------------------------------------------------------------------------------------------------------------------------------------
drop table if exists message_attachments;
drop table if exists messages;
drop table if exists chat_properties;
drop table if exists chat_participants;
drop table if exists chats;
drop table if exists sources;
drop table if exists registration_verification_codes;
drop table if exists users_authentication;
drop function if exists is_user_chat_participant;
drop function if exists is_user_admin;
------------------------------------------------------------------------------------------------------------------------------------------------
create table users_authentication(
	id int8 default ('x' || right(md5(to_char(current_timestamp, 'dd-mm-yyyy hh:mi:ss:us')), 8))::bit(63)::int8,
	nick varchar(20),
	name varchar,
	email varchar,
	passwd_hash varchar,
	devices_token_list varchar[] default '{}'::varchar[],
    was_confirmed bool default false,

	primary key(id),
	constraint id_positive check( id > 0 ),
	constraint nick_uniq unique(nick),
	constraint email_uniq unique(email),
	constraint nick_spelling check (nick similar to '[a-za-z0-9@\_.]*'),
	constraint name_spelling check (name similar to '%[a-za-zа-яа-я ]%'),
	constraint filled check ( id is not null and name is not null and passwd_hash is not null and email is not null)
);
create index user_id
    on users_authentication (id);
------------------------------------------------------------------------------------------------------------------------------------------------
create table registration_verification_codes(
  id int8 references users_authentication(id),
  mailcode int4 not null,
  validtime timestamp default current_timestamp + interval '2 hours',
  attemptsmade int2 default 0
);
------------------------------------------------------------------------------------------------------------------------------------------------
create table sources(
	inner_uri varchar,
    is_public boolean default false,
	is_showable boolean default false,
	path_original varchar,
	path_thumbnail varchar default null,
	owner int8 default 404 references users_authentication on delete set default ,
	description varchar default null,
	meta varchar default null,

	primary key (inner_uri),
	constraint uri_not_null check(inner_uri is not null),
	constraint _unique_originalpath unique(path_original),
	constraint owner_exist check(owner is not null),
	constraint path_existence check(path_original is not null)
);
create unique index source_thumbnail
	on sources (path_thumbnail)
	where path_thumbnail is not null;
------------------------------------------------------------------------------------------------------------------------------------------------
create table chats(
	id int8,
	name varchar,
	creator int8 default 404 references users_authentication on delete set default,
	avatar varchar default null references sources on delete restrict,
	color_rgba int4 default 0,
	encoded boolean default false,

	primary key (id),
	constraint name_is_not_null check(name is not null),
	constraint encoded_is_not_null check(encoded is not null)
);
create index chats_id_ind
    on chats (id);
------------------------------------------------------------------------------------------------------------------------------------------------
create table chat_properties(
    id int8 references chats(id) on delete cascade not null,
    property varchar not null,
    user_agreed int8 references users_authentication on delete cascade not null,

    primary key (id, property, user_agreed)
);
create index chats_properties_ind
    on chat_properties (id, property);
------------------------------------------------------------------------------------------------------------------------------------------------
create table chat_participants(
    participant_id int8 references users_authentication on delete cascade,
    chat_id int8 references chats on delete cascade,
	is_admin boolean default false,

	constraint participant_id_is_not_null check (participant_id is not null),
	constraint chat_id_is_not_null check(chat_id is not null),
	constraint is_admin_is_not_null check(is_admin is not null)
);
create index chat_participants_chat_ind
	on chat_participants(chat_id);
create index chat_participants_user_ind
	on chat_participants(participant_id);

create function is_user_chat_participant(_user_id int8, _chat_id int8)
returns boolean as $$
declare passed boolean;
begin
        return exists( select '*' from chat_participants where chat_id = _chat_id and participant_id = _user_id);
end;
$$  language plpgsql;

create function is_user_admin(_user_id int8, _chat_id int8)
returns boolean as $$
declare passed boolean;
begin
        return exists( select '*' from chat_participants where chat_id = _chat_id and participant_id = _user_id and is_admin);
end;
$$  language plpgsql;
------------------------------------------------------------------------------------------------------------------------------------------------
create table messages(
    id int8,
	chat_attached_id int8 references chats(id) on delete cascade,
	author_id int8 references users_authentication(id) on delete cascade,
	sent_time timestamptz default current_timestamp::timestamptz,
	tag_list varchar[] default array[]::varchar[],
	body text default '',
	has_attached_file boolean default false not null,
	was_modified boolean default false,

	primary key (id),
	constraint time_unique unique (sent_time),
	constraint not_empty_message check (id is not null and chat_attached_id is not null and tag_list is not null
									   and (body is not null and body <> '' or has_attached_file)),
    constraint author_is_participant check(is_user_chat_participant(author_id, chat_attached_id) or author_id = 1)
);
create index chat_ind
    on messages(chat_attached_id);
create unique index message_ind
	on messages(id);
------------------------------------------------------------------------------------------------------------------------------------------------
create table message_attachments(
    chat_attached_id int8,
    message_attached_id int8,
	uri varchar references sources(inner_uri) on delete restrict
);