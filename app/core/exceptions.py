class UserNotFoundError(Exception):
    pass


class UserEmailAlreadyExistsError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


class ReviewNotFoundError(Exception):
    pass


class BookPermissionError(Exception):
    pass
