# Methods for interacting with the server

## Login

#### URL `/registration` -> *Create a user account.*
* **Arguments**
```
{
  "nick": "string",
  "password": "string",
  "email": "user@example.com",
  "name": "string"
}
```
* **Return value** - the id of the created account.

* **Exceptions**
    * Status code 501
    * Status code 422
#### URL `/login` -> *Authenticate a user.*
* **Arguments**
```
{
  "nick": "string",
  "password": "string"
}
```
* **Return value** - the id of the authenticated account.

* **Exceptions**
    * Status code 400
    * Status code 401
    * Status code 501

## User
#### URL `/users/get_user_info` -> *Obtain information about a user of the platform.*
* **Arguments**
```
{
  "nick": "string",
  "password": "string"
}
```
* **Return value** - the id of the authenticated account.

* **Exceptions**
    * Status code 404

## Chats
#### URL `/chats/get_info` -> *Obtain information about a chat.*
* **Arguments**
```
{
  "current_user": "string",
  "chat_id": "string"
}
```
* **Return value** - A dict containing the following keys:

    * name – The name of the chat.
    * avatar_id – the id of an image containing the chat's avatar.
    * colour – The RGB value of the chat's colour.
    * is_encrypted – whether the chat is encrypted.
    * is_personal – whether the chat is personal.
    * is_user_expandable – The value of the user_expandable property.
    * is_user_expandable_modified_by – The id of the user who last modified the user_expandable property.
    * is_non_admin – The value of the non_admin property.
    * is_non_admin_modified_by – The id of the user who last modified the non_admin property.
    * non_removable_messages – The value of the non_removable_messages property.
    * non_removable_messages_modified_by – The id of the user who last modified the non_removable_messages property.
    * non_modifiable_messages – The value of the non_modifiable_messages property.
    * non_modifiable_messages_modified_by – The id of the user who last modified the non_modifiable_messages property.
    * auto_remove_messages – The value of the auto_remove_messages property.
    * auto_remove_messages_modified_by – The id of the user who last modified the auto_remove_messages property.
    * auto_remove_period – The lifetime of a message before it is automatically deleted.
    * digest_messages – The value of the digest_messages property (AutoLoggingMessages).
    * digest_messages_modified_by – The id of the user who last modified the digest_messages property.
    * admins – A list containing the user ids of the chat's admins.
    * users – A list containing the ids of the chat's participants who are not admins.
    * tags – A list containing all tags used in this chat.
    * attachments – A list containing the ids of all attachments of this chat's messages.
    * last_message_id – the id of the latest message in this chat, or None if there are no messages.

* **Exceptions**
    * Status code 401
    * Status code 404

#### URL `/chats/add_user` -> *Add a user to the chat with the given id.*
* **Arguments**

> **In query** `user_to_add: string` +
```
{
  "current_user": "string",
  "chat_id": "string"
}
```
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/remove_user` -> *Remove a user from the chat with the given id.*
* **Arguments**
```
{
  "info": {
    "current_user": "string",
    "chat_id": "string"
  },
  "user_to_remove": "string"
}
```
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/make_user_admin` -> *Make a user an admin of the given chat.*
* **Arguments**

> **In query** `target_user: string`
```
{
  "current_user": "string",
  "chat_id": "string"
}
```
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/create` -> *Create a new chat.*
* **Arguments**
```
{
  "current_user": "string",
  "name": "string",
  "colour": 0,
  "is_encrypted": false,
  "is_personal": false,
  "is_user_expandable": false,
  "is_non_admin": false,
  "non_removable_messages": false,
  "non_modifiable_messages": false,
  "auto_remove_messages": false,
  "auto_remove_period": 0,
  "digest_messages": false
}
```
* **Return value** - the same as get_info.

* **Exceptions**
    * Status code 401

#### URL `/chats/create_personal` -> *Create a personal chat with another user.*
* **Arguments**
> **In query** `current_user: string, user2: string`
* **Return value** - the same as get_info.

* **Exceptions**
    * Status code 401

#### URL `/chats/set_non_admin` -> *Set the value of the non_admin property*
* **Arguments**
> **In query** `current_user: string, chat_id: string, value: bool`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/set_user_expandable` -> *Set the value of the user_expandable property*
* **Arguments**
> **In query** `current_user: string, chat_id: string, value: bool`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/set_non_removable_messages` -> *Set the value of the non_removable_messages property*
* **Arguments**
> **In query** `current_user: string, chat_id: string, value: bool`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/set_non_modifiable_messages` -> *Set the value of the non_modifiable_messages property*
* **Arguments**
> **In query** `current_user: string, chat_id: string, value: bool`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/set_auto_remove_messages` -> *Set the value of the auto_remove_messages property*
* **Arguments**
> **In query** `current_user: string, chat_id: string, value: bool`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/set_digest_messages` -> *Set the value of the digest_messages property*
* **Arguments**
> **In query** `current_user: string, chat_id: string, value: bool`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/get_message` -> *Get the contents of a message.*
* **Arguments**
> **In query** `current_user: string, message_id: string`
* **Return value** - a dict containing the following keys:

    * id – The id of the message.
    * chat_id – The id of the chat to which this message belongs.
    * time – The time when the message was sent. Represented by a datetime object.
    * author_id – The id of the user who sent the message.
    * body – The body of the message.
    * tags – The list of tags of this message.
    * attachments – A list containing the ids of this message's attachments.

* **Exceptions**
    * Status code 401
    * Status code 404

#### URL `/chats/get_message_range` -> *Retrieve a range of messages.*
* **Arguments**
> **In query** `current_user: string, lower_id: string, upper_id:string, limit: int`
* **Return value** - A list of messages in the requested range in chronological order (from oldest to newest).

* **Exceptions**
    * Status code 401
    * Status code 404

#### URL `/chats/send_message` -> *Send a message to the specified chat.*
* **Arguments**
> **In query** `current_user: string, chat_id: string, body: string`
* **Return value** - the sent message.

* **Exceptions**
    * Status code 401

#### URL `/chats/edit_message` -> *Edit a message.*
* **Arguments**
> **In query** `current_user: string, chat_id: string, body: string`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/delete_message` -> *Delete a message.*
* **Arguments**
> **In query** `current_user: string, message_id: string`
* **Return value** - JSON string `{'result': result}`.

* **Exceptions**
    * Status code 401

#### URL `/chats/get_chats_for_user` -> *Retrieve the list of chats for a user.*
* **Arguments**
> **In query** `user_id: string`
* **Return value** - a list of ids of the chats in which the user is participating.

* **Exceptions**
    * Status code 401

#### URL `/chats/get_messages_with_tag` -> *Retrieve all messages with the specified tag from the specified chat*
* **Arguments**
> **In query** `current_user: string, chat_id: string, tag: string`
* **Return value** - a list of messages.

* **Exceptions**
    * Status code 401