class event(tuple):

    def __new__(self, *value):
        if len(value) == 1:
            if isinstance(value, tuple):
                value = value[0]
            if isinstance(value, str):
                value = (value,)

        ret = tuple.__new__(self, value)
        ret.processed = False
        return ret

    def add_leader(self, leader):
        return self.__class__(leader) + self

    def add_head(self, head):
        return self.__class__(head, self)

    def grow_head(self, head):
        pre = self.__class__(head)
        if len(self) == 0:
            return head
        return self.__class__(pre + self.__class__(self[0]), *self[1:])

    def match_leader(self, leader):
        leader = self.__class__(leader)
        if len(leader) > len(self):
            return None

        for this, that in zip(self, leader):
            if this != that:
                return None

        return self[len(leader):]

    def match(self, e):
        return self.__class__(e) == self

    def match_head(self, head):
        if len(self) == 0:
            return None

        myhead = self.__class__(self[0])

        if myhead.match_leader(head) is not None:
            if len(self) == 2:
                ret = self.__class__(self[1])

            else:
                ret = self[1:]

            return ret

        return None

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.__class__(tuple.__getitem__(self, index))

        else:
            return tuple.__getitem__(self, index)

    def __getslice__(self, start, end):
        return self.__class__(tuple.__getslice__(self, start, end))

    def __add__(self, other):
        return self.__class__(tuple.__add__(self, other))

    def __str__(self):
        if len(self) == 1:
            return self[0]

        return tuple.__str__(self)


class exception(event):
    def __new__(self, *value):
        ret = event.__new__(self, *value)
        ret.cleared = False
        return ret
