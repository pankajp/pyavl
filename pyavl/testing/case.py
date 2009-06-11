'''
Created on Jun 10, 2009

@author: pankaj
'''
import unittest
from pyavl.case import Case
from pyavl.geometry import Geometry

class Test(unittest.TestCase):


    def setUp(self):
        geometry = Geometry()
        self.case = Case(casename='testCase', mach_no=0.0, symmetry=(0,0,0.0), ref_area=9.0, ref_chord=0.9, ref_span=10.0, ref_cg=(0.5,0.0,0.0), geometry=geometry)

    def tearDown(self):
        pass


    def test_file_write(self):
        file = open('testcase.avl', 'w')
        self.case.write_input_file(file)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_file_write']
    unittest.main()