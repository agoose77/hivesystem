import sys

python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)

if python2:
    mytype = type
    myobject = object
elif python3:
    cache = set()

    class mytype(type):
        def __new__(metacls, name, bases, dic, **kargs):
            meta = type
            remcache = False
            if metacls not in cache:
                cache.add(metacls)
                remcache = True
                if "__metaclass__" in dic:
                    meta = dic["__metaclass__"]
                else:
                    for b in bases:
                        if hasattr(b, "__metaclass__"):
                            meta = b.__metaclass__
                            break
            if meta is mytype:
                # print("=MYTYPE!", name)
                ret = type(name, bases, dic)
            elif meta is type:
                # print("=TYPE!", name)
                ret = type.__new__(metacls, name, bases, dic, **kargs)
            else:
                # print("=META",meta,metacls)
                ret = meta.__new__(meta, name, bases, dic, **kargs)
            ret.__metaclass__ = meta
            if remcache: cache.remove(metacls)
            # print("DONE", name)
            return ret

    exec("class myobject(object,metaclass=mytype):pass")
