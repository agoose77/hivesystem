import bee
from bee.segments import *


class iterate(bee.worker):
    iterator = None
    iterable = antenna("pull", ("object", "iterable"))
    b_iterable = buffer("pull", ("object", "iterable"))
    connect(iterable, b_iterable)
    trig_iterable = triggerfunc(b_iterable, "update")
    outp = output("pull", "object")
    v_outp = variable("object")
    connect(v_outp, outp)

    def make_iterator(self):
        self.trig_iterable()
        for v in self.b_iterable:
            yield v

    @modifier
    def iterate(self):
        if self.iterator is None: self.iterator = self.make_iterator()
        try:
            self.v_outp = self.iterator.next()
        except StopIteration:
            self.iterator = self.make_iterator()
            self.v_outp = self.iterator.next()

    pretrigger(v_outp, iterate)
