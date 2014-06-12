class event(tuple):
    def __new__(self, *value):
        if len(value) == 1:
            if isinstance(value, tuple): value = value[0]
            if isinstance(value, str): value = (value,)
        ret = tuple.__new__(self, value)
        ret.processed = False
        return ret

    def add_leader(self, leader):
        return type(self)(leader) + self

    def add_head(self, head):
        return type(self)(head, self)

    def grow_head(self, head):
        pre = type(self)(head)
        if len(self) == 0: return head
        return type(self)(pre + type(self)(self[0]), *self[1:])

    def match_leader(self, leader):
        leader = type(self)(leader)
        if len(leader) > len(self): return None
        for s, p in zip(self, leader):
            if s != p: return None
        return self[len(leader):]

    def match(self, e):
        return type(self)(e) == self

    def match_head(self, head):
        if len(self) == 0: return None
        myhead = type(self)(self[0])
        if myhead.match_leader(head) is not None:
            ret = self[1:]
            if len(self) == 2: ret = type(self)(self[1])
            return ret
        return None

    def __getitem__(self, n):
        if isinstance(n, slice):
            return type(self)(tuple.__getitem__(self, n))
        else:
            return tuple.__getitem__(self, n)

    def __getslice__(self, start, end):
        return type(self)(tuple.__getslice__(self, start, end))

    def __add__(self, other):
        return type(self)(tuple.__add__(self, other))

    def __str__(self):
        if len(self) == 1: return self[0]
        return tuple.__str__(self)


class exception(event):
    def __new__(self, *value):
        ret = event.__new__(self, *value)
        ret.cleared = False
        return ret
