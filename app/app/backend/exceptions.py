class NotInitialised(Exception):
    pass


class NickTaken(Exception):
    pass


class EmailTaken(Exception):
    pass


class AuthenticationError(Exception):
    pass


class PermissionDenied(Exception):
    pass


class ObjectNotFound(Exception):
    pass


class InvalidRange(Exception):
    pass