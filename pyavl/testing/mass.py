'''
Created on Jun 26, 2009

@author: pankaj
'''
import unittest
from pyavl import mass


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_from_file(self):
        massobj = mass.Mass.mass_from_file('allegro.mass')
        print massobj.traits()
        
    def test_to_file(self):
        massobj = mass.Mass.mass_from_file('allegro.mass')
        file = open('allegro.test.mass','w')
        massobj.write_mass_file(file)
        
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_from_file']
    unittest.main()