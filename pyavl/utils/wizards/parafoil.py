'''
Created on Jul 13, 2009

@author: pankaj
'''

from pyavl.geometry import Section, SectionAFILEData, Geometry, Surface, SectionData
from pyavl.ui.geometry_viewer import GeometryViewer

import numpy

from enthought.traits.api import *
from enthought.traits.ui.api import *

class ParafoilWizard(HasTraits):
    span = Float(7.5)
    chord = Float(3.75)
    number_of_cells = Int(9)
    dihedral_angle = Float(40)
    sectiondata = Instance(SectionData, SectionAFILEData(filename='/opt/idearesearch/pyavl/testcase/avl_case/clarky.dat'))
    def get_surface(self):
        num_sections = (self.number_of_cells+1) // 2
        dihedral_angle_r = self.dihedral_angle*numpy.pi/180
        sections = []
        y = numpy.linspace((self.number_of_cells%2)/2.0, self.number_of_cells/2.0, num_sections)/self.number_of_cells
        for i,theta in enumerate(dihedral_angle_r*y):
            le = numpy.array([0, self.span*numpy.sin(theta)/2/numpy.sin(dihedral_angle_r), -self.span*(1-numpy.cos(theta))/2.0/numpy.sin(dihedral_angle_r)])
            sections.append(Section(leading_edge=le, chord=self.chord, type=self.sectiondata.type, data=self.sectiondata))
        surface = Surface(name='Parafoil', yduplicate=0, sections=sections)
        return surface


if __name__ == '__main__':
    import sys
    from pyavl.case import Case
    file = open('/opt/idearesearch/avl/runs/bd.avl')
    case = Case.case_from_input_file(file)
    pw = ParafoilWizard()
    pw.configure_traits()
    surface = pw.get_surface()
    #surface.configure_traits()
    geometry = Geometry(surfaces=[surface])
    #geometry.configure_traits()
    g = GeometryViewer(geometry=geometry)
    g.configure_traits()
    surface.write_to_file(sys.stdout)