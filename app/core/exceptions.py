class BooklyException(Exception):
    """This is the base class for all bookly errors"""

    pass


class UserNotFoundError(BooklyException):
    pass


class UserEmailAlreadyExistsError(BooklyException):
    pass


class BookNotFoundError(BooklyException):
    pass


class ReviewNotFoundError(BooklyException):
    pass


class BookPermissionError(BooklyException):
    pass


class TagNotFoundError(BooklyException):
    pass


class TagAlreadyExistsError(BooklyException):
    pass
