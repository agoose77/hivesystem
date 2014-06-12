class mstr(object):
    def __init__(self, string):
        if isinstance(string, mstr):
            self.value = string.value
        else:
            self.value = str(string)
