class StringValue(object):
    """Container of str object

    Used to effect mutable string reference
    """

    def __init__(self, string):
        if isinstance(string, StringValue):
            self.value = string.value

        else:
            self.value = str(string)
