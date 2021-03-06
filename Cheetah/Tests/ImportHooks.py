#!/usr/bin/env python

from glob import glob
import os
import shutil
import sys
import unittest
import Cheetah.ImportHooks


ImportHooksTemplatesDir = os.path.join(
    os.path.dirname(__file__), 'ImportHooksTemplates')


def setUpModule():
    sys.path.append(ImportHooksTemplatesDir)


def tearDownModule():
    assert sys.path[-1] == ImportHooksTemplatesDir
    del sys.path[-1]


def _cleanup():
    py_files = os.path.join(ImportHooksTemplatesDir, '*.py')
    pyc_files = py_files + 'c'
    for fname in glob(py_files) + glob(pyc_files):
        os.remove(fname)
    __pycache__ = os.path.join(ImportHooksTemplatesDir, '__pycache__')
    if os.path.isdir(__pycache__):
        shutil.rmtree(__pycache__)


def _exec(code, _dict):
    exec(code, _dict)


class ImportHooksTest(unittest.TestCase):
    def setUp(self):
        _cleanup()

    def test_CheetahDirOwner(self):
        templates = list(sorted(os.listdir(ImportHooksTemplatesDir)))
        self.assertListEqual(templates, ['index.tmpl', 'layout.tmpl'])

        cdo = Cheetah.ImportHooks.CheetahDirOwner(ImportHooksTemplatesDir)
        index_mod = cdo.getmod('index')
        templates = os.listdir(ImportHooksTemplatesDir)
        self.assertIn('index.py', templates)
        self.assertNotIn('layout.py', templates)

        index_co = index_mod.__co__
        del index_mod.__co__
        self.assertRaises(ImportError, _exec, index_co, index_mod.__dict__)

        cdo.getmod('layout')  # Compiled to layout.py and .pyc
        self.assertIn('layout.py', os.listdir(ImportHooksTemplatesDir))

    def test_ImportHooks(self):
        templates = os.listdir(ImportHooksTemplatesDir)
        self.assertNotIn('index.py', templates)
        self.assertNotIn('layout.py', templates)
        Cheetah.ImportHooks.install()
        from index import index  # noqa
        templates = os.listdir(ImportHooksTemplatesDir)
        self.assertIn('index.py', templates)
        self.assertIn('layout.py', templates)
        Cheetah.ImportHooks.uninstall()


if __name__ == '__main__':
    unittest.main()
