'''
Created on Jun 8, 2009

@author: pankaj
'''
import unittest
from pyavl import avl

class Test(unittest.TestCase):


    def setUp(self):
        self.avl = avl.AVL(cwd='/opt/idearesearch/avl/runs/')
        self.filename = '/opt/idearesearch/avl/runs/allegro.avl'

    def tearDown(self):
        self.avl.avl.close(True)


    def test_init(self):
        index = self.avl.avl.expect(self.avl.patterns['/'])
        if index == 0:
            #print self.avl.avl.before
            pass
        else:
            #print index
            pass
            
    def test_load_case(self):
        self.avl.load_case_from_file(self.filename)
        
            
    def test_runcase_init(self):
        self.avl.load_case_from_file(self.filename)
        runcase = avl.RunCase.get_case_from_avl(self.avl.avl, 1)
        assert runcase is not None
        
    def test_avl_ui(self):
        self.avl.load_case_from_file(self.filename)
        #self.avl.configure_traits()
    
    def test_param_modify(self):
        self.avl.load_case_from_file(self.filename)
        rc = self.avl.run_cases[0]
        p = rc.parameters['bank']
        rc.parameters['bank'].value = 2.2
        assert 'bank' in rc.parameters
        assert rc.parameters['bank'].value == 2.2
    
    def test_constraint_modify(self):
        self.avl.load_case_from_file(self.filename)
        rc = self.avl.run_cases[0]
        c = rc.constraints
        print c
        c['alpha'] = avl.Constraint(name='alpha', constraint_name='alpha', cmd='A', pattern='alpha', value=1.1)
        assert c['alpha'].value == 1.1
        assert c['alpha'].name == 'alpha'
        assert c['alpha'].pattern == 'alpha'
        #p = rc.parameters_info['bank']
        #rc.parameters['bank'] = 2.2
        #assert 'bank' in rc.parameters
        #assert rc.parameters['bank'] == 2.2
    
        
    def test_runcase_output(self):
        self.avl.load_case_from_file(self.filename)
        rc = self.avl.run_cases[0]
        out = rc.get_run_output()
        print out
        print len(out)
        
    def test_eigenmode_output(self):
        self.avl.load_case_from_file(self.filename)
        rc = self.avl.run_cases[0]
        print rc.parameters.keys()
        rc.parameters['velocity'].value = 100.0
        print rc.parameters['velocity'].value
        out = rc.get_modes()
        print [o.eigenvalue for o in out]
        print 'num modes:', len(out)
        #assert len(out) == 8
    
    def test_system_matrix(self):
        self.avl.load_case_from_file(self.filename)
        rc = self.avl.run_cases[0]
        print rc.parameters.keys()
        rc.parameters['velocity'].value = 100.0
        print rc.parameters['velocity'].value
        out = rc.get_system_matrix()
        print out
        print out.matrix
        print 'matrix shape', out.matrix.shape
    
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_init']
    unittest.main()
    