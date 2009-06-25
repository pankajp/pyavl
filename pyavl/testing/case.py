'''
Created on Jun 10, 2009

@author: pankaj
'''
import unittest
from pyavl.case import Case, filter_lines
from pyavl.geometry import Geometry, Surface, Section, SectionAFILEData

class Test(unittest.TestCase):

    def setUp(self):
        geometry = Geometry()
        surface1 = Surface(name='surface 1', cvortices=[20,1.0], scale=[1.0,1.0,1.0], index=1, yduplicate=1.0)
        section1data = SectionAFILEData(filename='/opt/idearesearch/avl/runs/ag42d.dat')
        section1 = Section(type='airfoil data file', data=section1data)
        geometry.surfaces.append(surface1)
        self.case = Case(casename='testCase', mach_no=0.0, symmetry=[0,0,0.0], ref_area=9.0, ref_chord=0.9, ref_span=10.0, ref_cg=[0.5,0.0,0.0], geometry=geometry)
        self.test_avl_case = 'allegro'

    def tearDown(self):
        pass

    def test_file_write(self):
        file = open(self.test_avl_case+'.avl', 'w')
        self.case.write_input_file(file)
    
    def test_file_read(self):
        file = open('/opt/idearesearch/avl/runs/'+self.test_avl_case+'.avl')
        case = Case.case_from_input_file(file)
        file.close()
        file = open('read_test_write.avl', 'w')
        case.write_input_file(file)
        file.close()
    
    def test_filter_lines(self):
        file = open('/opt/idearesearch/avl/runs/'+self.test_avl_case+'.avl')
        lines = filter_lines(file.readlines())
        f2 = open('filter_lines.avl', 'w')
        f2.write('\n'.join(lines))
        f2.close()
        file.close()
        file = open('filter_test.avl','w')
        file.write('\n'.join(lines))
        file.close()
    
    def test_ui(self):
        file = open('/opt/idearesearch/avl/runs/'+self.test_avl_case+'.avl')
        self.case = Case.case_from_input_file(file)
        import sys
        self.case.configure_traits()
        #self.case.geometry.surfaces[0].write_to_file(sys.stdout)
        
        #self.case.geometry.configure_traits()
        #self.case.geometry.surfaces[0].configure_traits()
        #self.case.geometry.write_to_file(sys.stdout)
        from pyavl.ui.geometry_viewer import GeometryViewer
        g = GeometryViewer(geometry=self.case.geometry)
        g.configure_traits(scrollable=True)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_file_write']
    unittest.main()