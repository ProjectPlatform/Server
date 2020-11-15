This document describes the functions in the backend package. All exceptions are in the backend.exceptions module.

# `async backend.init(settings: Settings)`
Initialise the database connection. This function must be called during application startup.

## Arguments
- settings – An object of type settings.Settings that holds the connection information.

# backend.user
## `async register(nick: str, password: str, email: EmailStr, name: str)`
Create a user account.

### Arguments
- nick – The nick of the user.
- password – The password of the user.
- email – The email of the user.
- name – The full name of the user.
### Return value
The id of the created account.

### Exceptions
- NickTaken – If a user with the given nick already exists.
- EmailTaken – If a user with the given email already exists.
## `async authenticate(nick: str, password: str) -> str`
Authenticate a user.

### Arguments
- nick – The nick of the user.
- password – The password of the user.
### Return value
The id of the authenticated account.

### Exceptions
- AuthenticationError – If the provided nick and password do not match any account in the system.
## `async get_user_info(current_user: Optional[str], user_id: str) -> Dict[str, Any]`
Obtain information about a user of the platform.

### Arguments
- current_user – The id of the currently logged in user.
- user_id – The id of the user whos info we want to see.
### Return value
A dict containing the following keys:

- nick – The nick of the user.
- name – The full name of the user.
- avatar_id – The id of an image containing the users avatar. Can be None.
### Exceptions
- ObjectNotFound – If there is no user with the given id.
# backend.chat
## `async get_info(current_user: str, chat_id: str) -> Dict[str, Any]`
Obtain information about a chat.

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
### Return value
A dict containing the following keys:
- name – The name of the chat.
- avatar_id – the id of an image containing the chat's avatar.
- colour – The RGB value of the chat's colour.
- is_encrypted – whether the chat is encrypted.
- is_personal – whether the chat is personal.
- is_user_expandable – The value of the user_expandable propperty.
- is_user_expandable_modified_by – The id of the user who last modified the user_expandable propperty.
- is_non_admin – The value of the non_admin propperty.
- is_non_admin_modified_by – The id of the user who last modified the non_admin propperty.
- non_removable_messages – The value of the non_removable_messages propperty.
- non_removable_messages_modified_by – The id of the user who last modified the non_removable_messages propperty.
- non_modifiable_messages – The value of the non_modifiable_messages propperty.
- non_modifiable_messages_modified_by – The id of the user who last modified the non_modifiable_messages propperty.
- auto_remove_messages – The value of the auto_remove_messages propperty.
- auto_remove_messages_modified_by – The id of the user who last modified the auto_remove_messages propperty.
- auto_remove_period – The lifetime of a message before it is automatically deleted.
- digest_messages – The value of the digest_messages propperty (AutoLoggingMessages).
- digest_messages_modified_by – The id of the user who last modified the digest_messages propperty.
- admins – A list containing the user ids of the chat's admins.
- users – A list containing the ids of the chat's participents who are not admins.
- tags – A list containing all tags used in this chat.
- attachments – A list containing the ids of all attachments of this chat's messages.
- last_message_id – the id of the latest message in this chat, or None if there are no messages.
### Exceptions
- ObjectNotFound – If there is no chat with the given id.
- PermissionDenied – If the current user is not a participent of this chat.
## `async add_user(current_user: str, chat_id: str, user_to_add: str) -> bool`
Add a user to the chat with the given id.

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- user_to_add – The id of the user who should be added to the chat.
### Return value
True on success, False if the user was already in the chat.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async remove_user(current_user: str, chat_id: str, user_to_remove: str) -> bool`
Remove a user from the chat with the given id.

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- user_to_remove – The id of the user who should be removed from the chat.
### Return value
True on success, False if the user wasn't in the chat.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async make_user_admin(current_user: str, chat_id: str, target_user: str) -> bool`
Make a user an admin of the given chat.

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- target_user – The id of the user who should be made an admin of the chat.
### Return value
True on success, False if the user isn't in the chat.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async create(    current_user: str,    name: str,    colour: int = 0,    is_encrypted: bool = False,    is_personal: bool = False,    is_user_expandable: bool = False,    is_non_admin: bool = False,    non_removable_messages: bool = False,    non_modifiable_messages: bool = False,    auto_remove_messages: bool = False,    auto_remove_period: Optional[int] = None,    digest_messages: bool = False,) -> Dict[str, Any]`
Create a new chat.

### Arguments
The meanings of the arguments are the same as the ones  described in the return value of backend.chat.get_info. However, is_personal should always be False (see the next function).

### Return value
All the information for the created chat. The same as get_info.

## `async create_personal(current_user: str, user2: str) -> Dict[str, Any]`
Create a personal chat with another user.

### Arguments
- current_user – The id of the currently logged in user.
- user2 – The id of the other user who will be in this chat.
### Return value
See create.

### Exceptions
- PermissionDenied – If there already exists a personal chat with these users.

## `async set_non_admin(current_user: str, chat_id: str, value: bool) -> bool`
Set the value of the non_admin propperty

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- value – The new value of the propperty
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async set_user_expandable(current_user: str, chat_id: str, value: bool) -> bool`
Set the value of the user_expandable propperty

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- value – The new value of the propperty
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async set_non_removable_messages(current_user: str, chat_id: str, value: bool) -> bool`
Set the value of the non_removable_messages propperty

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- value – The new value of the propperty
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async set_non_modifiable_messages(current_user: str, chat_id: str, value: bool) -> bool`
Set the value of the non_modifiable_messages propperty

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- value – The new value of the propperty
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async set_auto_remove_messages(current_user: str, chat_id: str, value: bool, period: Optional[int]) -> bool`
Set the value of the auto_remove_messages propperty

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- value – The new value of the propperty
- period – The auto_remove period.
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async set_digest_messages(current_user: str, chat_id: str, value: bool) -> bool`
Set the value of the digest_messages propperty

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- value – The new value of the propperty
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async get_message(current_user: str, message_id: str)`
Get the contents of a message.

### Arguments
- current_user – The id of the currently logged in user.
- message_id – The id of the message
### Return value
A dict containing the following keys:

- id – The id of the message.
- chat_id – The id of the chat to which this message belongs.
- time – The time when the message was sent. Represented by a datetime object.
- author_id – The id of the user who sent the message.
- body – The body of the message.
- tags – The list of tags of this message.
- attachments – A list containing the ids of this message's attachments.
### Exceptions
- ObjectNotFound – If there is no message with the given id.
- PermissionDenied – If the current user is not a participent of the chat to which the message belongs.
## `async get_message_range(    current_user: str, lower_id: Optional[str], upper_id: Optional[str], limit: int = 50) -> List[Dict[str, Any]]`
Retrieve a range of messages.

### Arguments
- current_user – The id of the currently logged in user.
- lower_id – The id of the first message in the range, or None for the first message in the chat.
- upper_id – The id of the last message in the range, or None for the last message in the chat.
- limit – The maximum amount of messages to return.
Note that lower_id and upper_id cannot be None at the same time.

### Return value
A list of messages in the requested range in chronological order (from oldest to newest). See the return value of get_message for further details.

### Exceptions
- InvalidRange – If the provided messages don't form a range, for example if they are from different chats or if the first message is newer than the last one.
- PermissionDenied – If the requested range belongs to a chat in which the current user doesn't participate.
## `async send_message(    current_user: str,    chat_id: str,    body: str,    attachments: Optional[List[Tuple[int, str]]] = None,    tags: Optional[List[str]] = None,) -> Dict[str, Any]`
Send a message to the specified chat.

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- body – The body of the message.
- attachments – A list of tuples of the form (type, id), where type is chat.ATTACHMENT_IMAGE or chat.ATTACHMENT_DOCUMENT and id is the id of the image/document in the attachment.
- tags – A list of the tags of this message, represented as strings.
### Return value
The sent message. See the return value of get_message for further details.

### Exceptions
- PermissionDenied – If the current user is trying to send a message to a chat they are not participating in.
## `async edit_message(    current_user: str,    message_id: str,    body: str,    attachments: Optional[List[Tuple[int, str]]],    tags: Optional[List[str]],) -> bool`
Edit a message.

### Arguments
- current_user – The id of the currently logged in user.
- message_id – The id of the message
- body – The body of the message.
- attachments – A list of tuples of the form (type, id), where type is chat.ATTACHMENT_IMAGE or chat.ATTACHMENT_DOCUMENT and id is the id of the image/document in the attachment.
- tags – A list of the tags of this message, represented as strings.
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async delete_message(current_user: str, message_id: str) -> bool`
Delete a message.

### Arguments
- current_user – The id of the currently logged in user.
- message_id – The id of the message
### Return value
True on success.

### Exceptions
- PermissionDenied – If the current user does not have the permission to perform the action.
## `async get_chats_for_user(user_id: str) -> List[str]`
Retrieve the list of chats for a user.

### Arguments
- user_id – The id of the user.
### Return value
A list of ids of the chats in which the user is participating.

## `async get_messages_with_tag(current_user: str, chat_id: str, tag: str) -> List[Dict[str, Any]]`
retrieve all messages with the specified tag from the specified chat

### Arguments
- current_user – The id of the currently logged in user.
- chat_id – The id of the chat
- tag – the tag to search for.
### Return value
A list of messages. See get_message for further details.

### Exceptions
- PermissionDenied – If the current user doesn't participate in the specified chat.
