import bee
from bee.segments import *


class iterator(bee.worker):
    iterable = variable(("object", "iterable"))
    parameter(iterable)
    iterator = None
    outp = output("pull", "object")
    v_outp = variable("object")
    connect(v_outp, outp)

    def make_iterator(self):
        for v in self.iterable:
            yield v

    @modifier
    def iterate(self):
        if self.iterator is None: self.iterator = self.make_iterator()
        self.v_outp = self.iterator.next()

    pretrigger(v_outp, iterate)
