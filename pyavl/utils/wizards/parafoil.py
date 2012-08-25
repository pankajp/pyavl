'''
Created on Jul 13, 2009

@author: pankaj
'''

from pyavl.geometry import Section, SectionAFILEData, Geometry, Surface, SectionData, SectionAIRFOILData
from pyavl.ui.geometry_viewer import GeometryViewer
from pyavl import runs_dir, src_dir

import numpy
import os

from enthought.traits.api import Float, Range, Instance, Int, HasTraits
from enthought.traits.ui.api import View, Item

class ParafoilWizard(HasTraits):
    span = Float(7.5)
    chord = Float(3.75)
    number_of_cells = Int(9)
    anhedral_angle = Float(40)
    sectiondata = Instance(SectionData, SectionAFILEData(filename=os.path.join(src_dir, 'testcase', 'avl_case', 'clarky.dat')))
    #le_cut = Range(0.0,1.0,0.0, desc='leading edge cut position')
    inlet_height = Range(0.0, 0.5, 0.1, desc='the height of the inlet cut')
    cut_angle = Range(90., 180., 135, desc='leading edge cut angle with the positive x axis')
    def get_surface(self):
        num_sections = (self.number_of_cells + 1) // 2
        anhedral_angle_r = self.anhedral_angle * numpy.pi / 180
        r = self.span / 2.0 / numpy.sin(anhedral_angle_r)
        sections = []
        y = numpy.linspace(self.number_of_cells % 2, self.number_of_cells, num_sections) / self.number_of_cells
        sectiondata = SectionAIRFOILData.get_clipped_section_data(self.sectiondata, self.inlet_height, self.cut_angle)
        filename = 'parafoil.dat'
        filename = os.path.abspath(filename)
        sectiondata.write_airfoil_file(filename, 'parafoil')
        if self.number_of_cells%2==1:
            le = numpy.zeros((3,))
            sectionafile = SectionAFILEData(filename=filename)
            sections.append(Section(leading_edge=le, chord=self.chord, type=sectionafile.type, data=sectionafile))
        for i, theta in enumerate(anhedral_angle_r * y):
            le = numpy.array([0, r * numpy.sin(theta), r * (numpy.cos(theta) - 1)])
            sectionafile = SectionAFILEData(filename=filename)
            sections.append(Section(leading_edge=le, chord=self.chord, type=sectionafile.type, data=sectionafile))
        surface = Surface(name='Parafoil', yduplicate=0, sections=sections)
        return surface
    traits_view = View('span','chord','number_of_cells','anhedral_angle',
                       Item('object.sectiondata.filename',label='section data file'),
                       'inlet_height','cut_angle')

if __name__ == '__main__':
    import sys
    from pyavl.case import Case
    from pyavl import runs_dir, join
    file = open(join(runs_dir, 'bd.avl'))
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