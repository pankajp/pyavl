'''
Created on Jun 8, 2009

@author: pankaj
'''
import unittest
from pyavl import avl

class Test(unittest.TestCase):


    def setUp(self):
        self.avl = avl.AVL()


    def tearDown(self):
        self.avl.avl.close(True)


    def test_init(self):
        index = self.avl.avl.expect(self.avl.patterns['/'])
        if index == 0:
            print self.avl.avl.before
        else:
            print index


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_init']
    unittest.main()