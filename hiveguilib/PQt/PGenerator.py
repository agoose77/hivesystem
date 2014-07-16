from __future__ import print_function, absolute_import

import spyder.formtools
import spyder.qtform
from spyder.qtform.anyQt.QtCore import QBuffer
from spyder.qtform.anyQt.QtUiTools import QUiLoader

from spyder.qtform import qtview, reserved as reserved0
reserved = set(reserved0)
reserved.add("value")

from spyder.qtform import qtview, reserved
from spyder.formtools import model, controller
import functools

from ..params import typemap

loader = None

from . import pythoncode
from . import objectlabel


def _PButtonCallback(callback, model, contains_reserved):
    val = model._get()
    if val is not None and contains_reserved:
        val = val.copy()
        for k in reserved:
            kk = k + "_"
            if kk in val:
                val[k] = val[kk]
                del val[kk]
    callback(val)


def remap_reserved(callback, params):
    params2 = params.copy()
    for k in reserved:
        kk = k + "_"
        if kk in params2:
            params2[k] = params2[kk]
            del params2[kk]
    callback(params2)


def viewupdate(m, con, *args):
    status = m._status(con)
    if hasattr(m, "_old_status") and status == m._old_status: return
    if status == "Status: OK" and not hasattr(m, "_old_status"):
        pass
    else:
        print(status)
    m._old_status = status


def PGenerator(paramnames, paramtypelist, paramvalues,
               update_callback, buttons=[], form_manipulators=[]
):
    global loader
    if loader is None: loader = QUiLoader()

    contains_reserved = False
    paramnames2 = paramnames

    for k in reserved:
        if k in paramnames:
            contains_reserved = True
            paramnames2 = [p if p != k else k + "_" for p in paramnames2]

    params = list(zip(paramnames2, paramtypelist))
    typetree = spyder.formtools.generate_typetree(params, typemap)
    form = spyder.core.spyderform(typetree)
    for subform in form._members.values():
        if subform.arraycount:
            subform.length = 10

    for buttonname, buttoncallback in buttons:
        form.add_button(buttonname, "before")

    for form_manipulator in form_manipulators:
        ret = form_manipulator(form)
        if ret is not None:
            form = ret

    m = model(typetree)
    con = controller(form, m)

    xml = spyder.qtform.xml(form=form)
    buf = QBuffer()
    buf.open(QBuffer.ReadWrite)
    buf.write(xml)
    buf.close()
    parwidget = loader.load(buf)

    for pname in paramnames:
        pname2 = pname
        if pname in reserved:
            pname2 = pname + "_"

        f = form._members[pname2]
        tt = f._typetree
        if hasattr(f, "type") and f.type == "object" or \
                        hasattr(tt, "fulltypename") and (tt.fulltypename == "object" or \
                                                                     tt.fulltypename[0] == "object"):
            f._disabled = True

    v = qtview.qtview(form)
    v._wrap(parwidget)

    for pname in paramnames:
        pname2 = pname
        if pname in reserved: pname2 = pname + "_"
        f = form._members[pname2]
        if hasattr(f, "type") and f.type == "pythoncode":
            widget = getattr(v, pname2).widget
            i = id(widget)
            if i in pythoncode.callbacks: continue
            pythoncode.callbacks.add(i)
            cb = functools.partial(pythoncode.highlight, widget)
            widget.textChanged.connect(cb)
            pythoncode.set_css(widget)

    # bind view to controller
    con._bind_view(v)
    #listen for model updates
    con._listen()

    if not len(paramvalues):
        #if there are no current param values, load the form defaults into the model
        con._sync_from_view()
    else:
        #else, set the current values into the model
        for pname, pvalue in paramvalues.items():
            pname2 = pname
            if pname in reserved: pname2 = pname + "_"
            if pvalue is not None:
                getattr(m, pname2)._set(pvalue)

    #synchronize
    con._sync_to_view()

    for pname in paramnames:
        pname2 = pname
        if pname in reserved: pname2 = pname + "_"
        f = form._members[pname2]
        if hasattr(f, "type") and f.type == "pythoncode":
            widget = getattr(v, pname2).widget
            code = None
            if hasattr(f, "value"):
                code = f.value
            elif hasattr(f, "default"):
                code = f.default
            if code is not None:
                widget.setPlainText(code)
                pythoncode.highlight(widget)

    for buttonindex, button in enumerate(buttons):
        buttonname, buttoncallback = button
        cb = functools.partial(_PButtonCallback, buttoncallback, m, contains_reserved)
        v.buttons[buttonindex].listen(cb)

    up = update_callback
    if contains_reserved: up = functools.partial(remap_reserved, update_callback)
    m._listen(up)

    con._sync_from_view()
    v.listen(functools.partial(viewupdate, m, con))

    return parwidget, con
