'''
Created on Jun 8, 2009

@author: pankaj
'''

import numpy
from enthought.traits.api import HasTraits, List, Str, Float, Range, Int, Dict, File,\
    Trait, Instance, Enum, Array, DelegatesTo, cached_property, Property
from enthought.traits.ui.api import View, Group, Item
from geometry import Geometry

def filter_lines(lines):
    ret = []
    for line in lines:
        index1 = line.find('#')
        index2 = line.find('!')
        index = min(index1, index2)
        if index < 0: index = max(index1, index2)
        if index >= 0:
            line = line[:index]
        line = line.strip()
        if len(line) > 0:
            ret.append(line)
    return ret

class Case(HasTraits):
    '''
    A class representing an avl input file
    '''
    casename = Str()
    mach_no = Float()
    symmetry = List(minlen=3, maxlen=3)
    ref_area = Float()
    ref_chord = Float()
    ref_span = Float()
    ref_cg = Array(numpy.float, (3,))
    CD_p = Float
    geometry = Instance(Geometry)
    
    traits_view = View(Item('casename'),
                       Item('mach_no'),
                       Item('symmetry'),
                       Item('ref_area'),
                       Item('ref_chord'),
                       Item('ref_span'),
                       Item('ref_cg'),
                       Item('CD_p')
                       )
    
    @cached_property
    def _get_geometries(self):
        return [self.geometry] if self.geometry is not None else []
    controls = DelegatesTo('geometry')
    
    def write_input_file(self, file):
        '''
        Write all the data in the case in the appropriate format as in input .avl file for the AVL program
        '''
        file.write(self.casename + '\n')
        file.write('#Mach no\n%f\n' % self.mach_no)
        file.write('#iYsym\tiZsym\tZsym\n%d\t%d\t%f\n' % tuple(self.symmetry))
        file.write('#Sref\tCref\tBref\n%f\t%f\t%f\n' % (self.ref_area, self.ref_chord, self.ref_span))
        file.write('#Xref\tYref\tZref\n%f\t%f\t%f\n' % tuple(self.ref_cg))
        if self.CD_p != 0.0:
            file.write('#CD_p profile drag coefficient\n%f\n' % self.CD_p)
        file.write('\n')
        file.write('#'*70)
        file.write('\n')
        self.geometry.write_to_file(file)
        file.write('')
    
    @classmethod
    def case_from_input_file(cls, file):
        '''
        return an instance of Case by reading its data from an input file
        '''
        lines = file.readlines()
        lines = filter_lines(lines)
        lineno = 0
        casename = lines[0]
        mach_no = float(lines[1].split()[0])
        symmetry = lines[2].split()
        symmetry = [int(symmetry[0]), int(symmetry[1]), float(symmetry[2])]
        ref_area, ref_chord, ref_span = [float(value) for value in lines[3].split()[:3]]
        ref_cg = [float(value) for value in lines[4].split()[:3]]
        lineno = 5
        try:
            CD_p = float(lines[5].split()[0])
            lineno = 6
        except ValueError:
            CD_p = 0.0
        geometry = Geometry.create_from_lines(lines, lineno)
        case = Case(casename=casename, mach_no=mach_no, symmetry=symmetry, ref_area=ref_area, ref_chord=ref_chord, ref_span=ref_span, ref_cg=ref_cg, CD_p=CD_p, geometry=geometry)
        return case
    
if __name__ == '__main__':
    file = open('/opt/idearesearch/avl/runs/allegro.avl')
    case = Case.case_from_input_file(file)
    #import sys
    case.configure_traits()
    #self.case.geometry.surfaces[0].write_to_file(sys.stdout)
    
    #self.case.geometry.configure_traits()
    #self.case.geometry.surfaces[0].configure_traits()
    #self.case.geometry.write_to_file(sys.stdout)
    from pyavl.ui.geometry_viewer import GeometryViewer
    print case.geometry, type(case.geometry)
    g = GeometryViewer(geometry=case.geometry)
    g.configure_traits(scrollable=True)
    