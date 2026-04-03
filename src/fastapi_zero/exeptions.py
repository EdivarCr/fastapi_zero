class DomainError(Exception):
    pass


class UserAlreadyExistsError(DomainError):
    def __init__(self, field: str = 'user'):
        self.field = field
        super().__init__(f'{field} already exists')


class UserNotFoundError(DomainError):
    def __init__(self, message: str = 'User not found'):
        super().__init__(message)


class ForbiddenError(DomainError):
    def __init__(self, message: str = 'Not enough permissions'):
        super().__init__(message)


class TodoNotFoundError(DomainError):
    def __init__(self, message: str = 'Task not found'):
        super().__init__(message)


class TodoNotInTrashError(DomainError):
    def __init__(self, message: str = 'Todo is not in trash'):
        super().__init__(message)


class InvalidCredentialsError(DomainError):
    def __init__(self, message: str = 'Incorrect username or password'):
        super().__init__(message)
