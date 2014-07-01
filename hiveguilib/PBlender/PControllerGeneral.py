import weakref
import logging
from ..HBlender.BlenderWidgets import *
from ..HBlender.BlenderTextWidget import BlenderTextWidget
from ..PGui.profiletypes import profiletypes, profiles_worker


class PControllerGeneral(object):
    label = "Worker"

    def __init__(self, parent):
        self._parent = weakref.ref(parent)
        self.visible = False
        self.widget = BlenderLayoutWidget(None)

        self.l_workerid = BlenderLabelWidget(self.widget, "%s ID" % self.label)
        self.widget.children.append(self.l_workerid)
        self.w_workerid = BlenderStringWidget(self.widget, "")
        self.widget.children.append(self.w_workerid)

        self.w_update = BlenderButtonWidget(self.widget, "Update ID")
        self.w_update.listen(self._update_id)
        self.widget.children.append(self.w_update)

        self.w_cancel = BlenderButtonWidget(self.widget, "Cancel")
        self.w_cancel.listen(self._cancel_update_id)
        self.widget.children.append(self.w_cancel)

        self.l_workertype = BlenderLabelWidget(self.widget, "%s Type" % self.label)
        self.widget.children.append(self.l_workertype)

        self.l_workertooltip = BlenderLabelWidget(self.widget, "%s Description" % self.label)
        self.widget.children.append(self.l_workertooltip)

        self.w_profile = BlenderOptionWidget(self.widget, "%s Profile" % self.label, [], advanced=True)
        self.widget.children.append(self.w_profile)
        self.profiles = profiles_worker
        self._update_profilewidget()
        self.w_profile.listen(self._update_profile)

        self._added = False
        self._updating = False
        self.has_profile = False

    def _update_profilewidget(self):
        self.w_profile.options = [v[0] for v in self.profiles]
        self.w_profile.option_names = [v[1] for v in self.profiles]
        parent = self._parent()
        if hasattr(parent, "_wim"):
            try:
                instance = parent._wim().get_workerinstance(self._workerid)
            except KeyError:
                return
            if "simplified" in instance.profiles:#
                self.w_profile.options.append("simplified")
                self.w_profile.option_names.append("Simplified")

    def _update_profile(self, profile):
        profile0 = profile
        if self._updating: return
        index = self.w_profile.get_index()
        if index == self._profile_index: return
        if self.has_profile:
            parent = self._parent()
            try:
                parent._wim().morph_worker(self._workerid, profile)
                self._profile_index = index
            except KeyError:
                profile = self.w_profile.options[self._profile_index - 1]
                self.w_profile.set(profile)
            self.w_profile.set(profile)

    def _update_id(self):
        new_workerid = self.w_workerid.value

        if new_workerid == self._workerid: return
        parent = self._parent()
        pwindow = parent._pwindow()
        pmanager = pwindow.pmanager()
        ok1 = parent.gui_renames_worker(new_workerid)
        if not ok1:
            # self.l_workerid.setText("<font color=red>%s ID</font>" % self.label)
            self.w_workerid.value = self._workerid  ###
            return
        if pmanager is not None:
            ok2 = pmanager.gui_renames_pwidget(self._workerid, new_workerid)
            assert ok2 == True
        self._workerid = new_workerid

    def _cancel_update_id(self):
        self.w_workerid.value = self._workerid

    def switch_profiles(self, newprofiles):
        self.profiles = newprofiles
        self._update_profilewidget()

    def set_values(self, workerid, workertype, profiletype, profile, tooltip):
        self.w_workerid.value = workerid
        self.l_workertype.text = "%s Type: %s" % (self.label, workertype)
        self.l_workertooltip.text = "%s Description: %s" % (self.label, tooltip)


        self._workerid = workerid
        self.l_workerid.text = "%s ID" % self.label
        newprofiles = profiletypes[profiletype]
        self.switch_profiles(newprofiles)

        self.has_profile = False
        if profile is not None:
            for i, pr in enumerate(self.w_profile.options):
                if pr == profile:
                    self._profile_index = i + 1
                    self.has_profile = True
                    break
        if not self.has_profile:
            self._profile_index = 0
        self._updating = True
        self.w_profile.set_index(self._profile_index)
        self._updating = False

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self, context, layout):
        if self.visible: self.widget.draw(context, layout)