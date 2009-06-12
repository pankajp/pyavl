'''
Created on Jun 10, 2009

@author: pankaj
'''
import unittest
from pyavl.case import Case, filter_lines
from pyavl.geometry import Geometry, Surface

class Test(unittest.TestCase):


    def setUp(self):
        geometry = Geometry()
        surface1 = Surface('surface 1', (20,1.0), scale=2.0)
        geometry.surfaces[surface1.name] = surface1
        self.case = Case(casename='testCase', mach_no=0.0, symmetry=(0,0,0.0), ref_area=9.0, ref_chord=0.9, ref_span=10.0, ref_cg=(0.5,0.0,0.0), geometry=geometry)

    def tearDown(self):
        pass


    def test_file_write(self):
        file = open('testcase.avl', 'w')
        self.case.write_input_file(file)
    
    def test_file_read(self):
        file = open('/opt/idearesearch/avl/runs/vanilla.avl')
        case = Case.case_from_input_file(file)
        case.write_input_file('vanilla_test.avl')
    
    def test_filter_lines(self):
        file = open('/opt/idearesearch/avl/runs/vanilla.avl')
        lines = filter_lines(file.readlines())
        file.close()
        file = open('filter_test.avl','w')
        file.write('\n'.join(lines))
        file.close()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_file_write']
    unittest.main()