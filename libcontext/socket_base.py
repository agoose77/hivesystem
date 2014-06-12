class socket_base:
    def __init__(self, function):
        self.function = function
        self.counter = 0

    def __fill__(self, *args, **kargs):
        self.function(*args, **kargs)
        self.counter += 1
