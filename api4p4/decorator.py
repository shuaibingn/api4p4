from functools import wraps


def check_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        self.connect()
        return func(*args, **kwargs)

    return wrapper
