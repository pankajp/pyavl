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
            
    def test_load_case(self):
        filename = '/opt/idearesearch/avl/runs/vanilla.avl'
        self.avl.load_case_from_file(filename)
        
            
    def test_runcase_init(self):
        filename = '/opt/idearesearch/avl/runs/vanilla.avl'
        self.avl.load_case_from_file(filename)
        runcase = avl.RunCase.get_case_from_avl(self.avl.avl, 1)
        
    def test_avl_ui(self):
        filename = '/opt/idearesearch/avl/runs/vanilla.avl'
        self.avl.load_case_from_file(filename)
        self.avl.configure_traits()
    
    def test_param_modify(self):
        filename = '/opt/idearesearch/avl/runs/vanilla.avl'
        self.avl.load_case_from_file(filename)
        rc = self.avl.run_cases[0]
        p = rc.parameters_info[0]
        rc.parameters[p] = 2.2
        v = None
        for parameter,val,unit in rc.parameters:
            if parameter == p:
                v = val
        assert v is not None
        assert v == 2.2
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_init']
    unittest.main()