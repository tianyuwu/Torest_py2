# coding:utf-8

import re
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

import time
import shutil
import unittest
import subprocess



class DummySubTest(object):
    def __enter__(self):
        pass

    def __exit__(self, type, value, trace):
        return False


class Tests(unittest.TestCase):
    process = []
    dir_lst = []
    dir_to_port = {}

    def _fake_subTest(self, i):
        return DummySubTest()

    @classmethod
    def tearDownClass(cls):
        '''for i in cls.process:
            i.kill()'''

        '''time.sleep(3)
        try:
            for name in cls.dir_lst:
                shutil.rmtree(name)
        except:
            pass'''

    def test_index(self):
        self.assertEqual(200, 200)



if __name__ == '__main__':
    unittest.main()