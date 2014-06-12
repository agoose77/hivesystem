import bee
from bee.segments import *


class gentuple(object):
    """
    Wraps a tuple or other iterable
    """

    def __new__(cls, wrapped_tuple):
        is_iterable = hasattr(wrapped_tuple, "__getitem__")
        if not is_iterable:
            raise TypeError("gentuple argument must be iterable")

        class gentuple(bee.worker):
            v_wrapped = variable(("object", "iterable", "tuple"))
            startvalue(v_wrapped, wrapped_tuple)
            value = output("pull", ("object", "iterable", "tuple"))
            connect(v_wrapped, value)

            @staticmethod
            def worker_length():
                class length(bee.worker):
                    v_length = variable("int")
                    startvalue(v_length, len(wrapped_tuple))
                    outp = output("pull", "int")
                    connect(v_length, outp)

                return length()

            @staticmethod
            def worker_item(index):
                class item(bee.worker):
                    v_item = variable("object")
                    startvalue(v_item, wrapped_tuple[index])
                    outp = output("pull", "object")
                    connect(v_item, outp)

                return item()

            @staticmethod
            def worker_getitem():
                class getitem(bee.worker):
                    inp = antenna("pull", "int")
                    b_inp = buffer("pull", "int")
                    trig_inp = triggerfunc(b_inp, "update")
                    connect(inp, b_inp)
                    outp = output("pull", "object")
                    v_outp = variable("object")
                    connect(v_outp, outp)

                    @modifier
                    def m_getitem(self):
                        self.trig_inp()
                        index = self.b_inp
                        item = wrapped_tuple[index]
                        self.v_outp = item

                    pretrigger(v_outp, m_getitem)

                return getitem()

            @staticmethod
            def worker_slice(start, end):
                class slice(bee.worker):
                    v_slice = variable(("object", "iterable", "tuple"))
                    startvalue(v_slice, wrapped_tuple[start:end])
                    outp = output("pull", ("object", "iterable", "tuple"))
                    connect(v_slice, outp)

                return slice()

            @staticmethod
            def worker_getslice():
                class getslice(bee.worker):
                    inp = antenna("pull", ("int", "int"))
                    b_inp = buffer("pull", ("int", "int"))
                    trig_inp = triggerfunc(b_inp, "update")
                    connect(inp, b_inp)
                    outp = output("pull", ("object", "iterable", "tuple"))
                    v_outp = variable(("object", "iterable", "tuple"))
                    connect(v_outp, outp)

                    @modifier
                    def m_getslice(self):
                        self.trig_inp()
                        start, end = self.b_inp
                        slice = wrapped_tuple[start:end]
                        self.v_outp = slice

                    pretrigger(v_outp, m_getslice)

                return getslice()

        return gentuple()
