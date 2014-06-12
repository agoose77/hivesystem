import bee
from bee.segments import *


class dictionary(object):
    metaguiparams = {"type": "type"}

    def __new__(cls, type):
        class dictionary(bee.worker):
            def place(self):
                self._dict = {}
                self.v_dic = self._dict

            def __setitem__(self, key, value):
                self._dict[key] = value

            def __getitem__(self, key):
                return self._dict[key]

            def __iter__(self):
                return self._dict.__iter__()

            def __len__(self):
                return self._dict.__len__()

            def __contains__(self, *args, **kwargs):
                return self._dict.__contains__(*args, **kwargs)

            def __delitem__(self, *args, **kwargs):
                return self._dict.__delitem__(*args, **kwargs)

            def keys(self): return self._dict.keys()

            def items(self): return self._dict.values()

            def clear(self): return self._dict.clear()

            def copy(self): return self._dict.copy()

            def pop(self, key): return self._dict.pop(key)

            def update(self, *args, **kwargs): return self._dict.update(*args, **kwargs)


            dic = output("pull", ("object", "dict"))
            v_dic = variable(("object", "dict"))
            connect(v_dic, dic)

            key = antenna("push", "id")
            v_key = variable("id")
            connect(key, v_key)

            setitem = antenna("push", ("id", type))
            v_setitem = variable(("id", type))
            connect(setitem, v_setitem)

            @modifier
            def do_setitem(self):
                key, value = self.v_setitem
                self[key] = value

            trigger(v_setitem, do_setitem)

            setvalue = antenna("push", type)
            v_setvalue = variable(type)
            connect(setvalue, v_setvalue)

            @modifier
            def do_setvalue(self):
                key = self.v_key
                value = self.v_setvalue
                self[key] = value

            trigger(v_setvalue, do_setvalue)

            getvalue = output("pull", type)
            v_getvalue = variable(type)
            connect(v_getvalue, getvalue)

            @modifier
            def do_getvalue(self):
                key = self.v_key
                value = self[key]
                self.v_getvalue = value

            pretrigger(v_getvalue, do_getvalue)

            # in-out mode
            inkey = antenna("push", "id")
            v_inkey = variable("id")
            connect(inkey, v_inkey)

            outvalue = output("push", type)
            b_outvalue = buffer("push", type)
            connect(b_outvalue, outvalue)
            trig_outvalue = triggerfunc(b_outvalue)

            @modifier
            def do_inout(self):
                out = self[self.v_inkey]
                self.b_outvalue = out
                self.trig_outvalue()

            trigger(v_inkey, do_inout)

        return dictionary


dictionary_str = dictionary("str")
dictionary_int = dictionary("int")
dictionary_float = dictionary("float")
dictionary_bool = dictionary("bool")
