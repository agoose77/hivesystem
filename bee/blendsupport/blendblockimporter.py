# Copyright 2013 Sjoerd de Vries.
# Adapted from the pure Python zipfile importer by Iain Wade and Guido van Rossum, copyright 2008, Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Order in which we probe the .blend data blocks.
# This is a list of (suffix, is_package) tuples.
_SEARCH_ORDER = [
    # Try .py first since that is most common.
    ('.py', False),
    ('/__init__.py', True),
]


class BlendImportError(ImportError):
    """Exception raised by blendblockimporter objects."""


import sys
import os
import types


class blendertexts:
    def __init__(self, getter):
        self._getter = getter

    def __contains__(self, key):
        key = key.replace(os.sep, '/')
        v = self._getter()
        return v and key in v

    def keys(self):
        v = self._getter()
        if v is None: return []
        return [key.replace('/', os.sep) for key in self._getter().keys()]

    def __getitem__(self, key):
        key = key.replace(os.sep, '/')
        v = self._getter()
        if v is None: raise KeyError
        return v[key].as_string()


ini_dict = {}
blendertext_dict = ini_dict


def textgetter():
    d = bpy.data
    if hasattr(d, "texts"): return d.texts


try:
    import bpy

    blendertext_dict = blendertexts(textgetter)
except ImportError:
    pass


class blendblockimporter:
    """A PEP-302-style importer that can import from .blend text datablocks

    Just insert or append this class (not an instance) to sys.path_hooks
    and you're in business.  Instances satisfy both the 'importer' and
    'loader' APIs specified in PEP 302.
    """

    datablocks = blendertext_dict

    def __init__(self, path_entry):
        """Constructor.

        Args:
          path_entry: The entry in sys.path.  This should be // to indicate
          the current .blend
        """
        global os
        #if os is None: os = sys.modules["os"] #BGE re-initialization, or something...
        if os is None: raise ImportError
        if not path_entry.startswith("//"): raise BlendImportError
        if self.datablocks is ini_dict: raise BlendImportError

        self.path_entry = path_entry

    def _get_info(self, fullmodname):
        """Internal helper for find_module() and load_module().

        Args:
          fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.

        Returns:
          A tuple (submodname, is_package, relpath) where:
            submodname: The final component of the module name, e.g. 'mail'.
            is_package: A bool indicating whether this is a package.
            relpath: The path to the module's source code within the .blend

        Raises:
          ImportError if the module is not found in the archive.
        """
        parts = fullmodname.split('.')
        submodname = parts[-1]
        modpath = '/'.join(parts)
        for suffix, is_package in _SEARCH_ORDER:
            relpath = modpath + suffix
            try:
                self.datablocks[relpath]
            except KeyError:
                pass
            else:
                return submodname, is_package, relpath
        msg = ('Can\'t find module %s in .blend %r' %
               (fullmodname, self.path_entry))
        ##logging.debug(msg)
        raise BlendImportError(msg)

    def find_module(self, fullmodname, path=None):
        """PEP-302-compliant find_module() method.

        Args:
          fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.
          path: Optional and ignored; present for API compatibility only.

        Returns:
          None if the module isn't found in the archive; self if it is found.
        """
        try:
            submodname, is_package, relpath = self._get_info(fullmodname)
        except ImportError:
            ##logging.debug('find_module(%r) -> None', fullmodname)
            return None
        else:
            ##logging.debug('find_module(%r) -> self', fullmodname)
            return self

    def load_module(self, fullmodname):
        """PEP-302-compliant load_module() method.

        Args:
          fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.

        Returns:
          The module object constructed from the source code.

        Raises:
          SyntaxError if the module's source code is syntactically incorrect.
          ImportError if there was a problem accessing the source code.
          Whatever else can be raised by executing the module's source code.
        """
        ##logging.debug('load_module(%r)', fullmodname)
        submodname, is_package, fullpath, source = self._get_source(fullmodname)
        code = compile(source, fullpath, 'exec')
        mod = sys.modules.get(fullmodname)
        if mod is None:
            mod = sys.modules[fullmodname] = types.ModuleType(fullmodname)
        mod.__loader__ = self
        f = fullpath
        if f.startswith('//'):
            f = f[2:]
            mod.__file__ = '//' + f.replace('/', os.sep)
        else:
            mod.__file__ = fullpath.replace('/', os.sep)
        mod.__name__ = fullmodname
        if is_package:
            f = mod.__file__
            if f.startswith('//'):
                f = f[2:]
                mod.__path__ = ['//' + os.path.dirname(f)]
            else:
                mod.__path__ = [os.path.dirname(f)]
        exec(code, mod.__dict__)
        return mod

    # Optional PEP 302 functionality.  See the PEP for specs.

    def get_data(self, fullpath):
        """Return (binary) content of a text datablock in the .blend"""
        required_prefix = self.path_entry
        if not fullpath.startswith(required_prefix):
            raise IOError('Path %r doesn\'t start with .blend identifier %r' %
                          (fullpath, required_prefix))
        relpath = fullpath[len(required_prefix):]
        try:
            return self.datablocks[relpath]
        except KeyError:
            raise IOError('Path %r not found in .blend' %
                          (relpath,))


    def _get_source(self, fullmodname):
        """Internal helper for load_module().

        Args:
          fullmodname: The dot-separated full module name, e.g. 'django.core.mail'.

        Returns:
          A tuple (submodname, is_package, fullpath, source) where:
            submodname: The final component of the module name, e.g. 'mail'.
            is_package: A bool indicating whether this is a package.
            fullpath: The path to the module's source code including the
              path to the current .blend (//).
            source: The module's source code.

        Raises:
          ImportError if the module is not found in the archive.
        """
        submodname, is_package, relpath = self._get_info(fullmodname)
        fullpath = self.path_entry + relpath
        source = self.datablocks[relpath]
        if hasattr(source, "decode"):
            source = source.decode("UTF-8")
        source = source.replace('\r\n', '\n')
        source = source.replace('\r', '\n')
        return submodname, is_package, fullpath, source

    def is_package(self, fullmodname):
        """Return whether a module is a package."""
        submodname, is_package, relpath = self._get_info(fullmodname)
        return is_package

    def get_code(self, fullmodname):
        """Return bytecode for a module."""
        submodname, is_package, fullpath, source = self._get_source(fullmodname)
        return compile(source, fullpath, 'exec')

    def get_source(self, fullmodname):
        """Return source code for a module."""
        submodname, is_package, fullpath, source = self._get_source(fullmodname)
        return source
