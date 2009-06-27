'''
Created on Jun 26, 2009

@author: pankaj
'''

import pexpect
import os
from enthought.traits.api import HasTraits, List, Float, Array, Tuple, Instance
from enthought.traits.ui.api import EnumEditor
import re
import numpy
from pyavl.case import filter_lines

class MassObject(HasTraits):
    mass = Float
    cg = Array(numpy.float, (3,))
    inertia_moment = Array(numpy.float, (3,))
    # I_xy I_xz i_yz
    cross_inertia = Array(numpy.float, (3,))
    
class Mass(HasTraits):
    lunit = Tuple((1.0, 'm')) # meters
    munit = Tuple((1.0, 'kg')) # kg
    tunit = Tuple((1.0, 's')) # seconds
    g = Float(9.81) # lunit / tunit**2
    rho = Float(1.225) # munit / lunit**3
    objects = List(Instance(MassObject))
    
    def write_mass_file(self, file):
        file.write('Lunit = %d %s\n' %(self.lunit[0], self.lunit[1]))
        file.write('Munit = %d %s\n' %(self.munit[0], self.munit[1]))
        file.write('Tunit = %d %s\n' %(self.tunit[0], self.tunit[1]))
        file.write('g = %d\n' %self.g)
        file.write('rho = %d\n' %self.rho)
        file.write('\n')
        file.write('#  mass   x     y     z      Ixx     Iyy     Izz   [ Ixy  Ixz  Iyz ]')
        for massobj in self.objects:
            file.write('%f\t' %(massobj.mass))
            file.write('%f %f %f\t' %(tuple(massobj.cg)))
            file.write('%f %f %f\t' %(tuple(massobj.inertia_moment)))
            file.write('%f %f %f\n' %(tuple(massobj.cross_inertia)))
        
    
    @classmethod
    def mass_from_file(cls, filename):
        file = open(filename)
        lines = file.readlines()
        file.close()
        lines = filter_lines(lines)
        traits = {}
        for i,line in enumerate(lines):
            match = re.match(r'(?P<name>\S+?)\s*?=\s*?(?P<value>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)\s*?(?P<unit>\S+)?$', line)
            if match is not None:
                name = match.group('name').lower()
                if name[1:] == 'unit':
                    unit = match.group('unit')
                    unit = unit if unit is not None else ''
                    value = float(match.group('value'))
                    traits[name] = value, unit
                else:
                    value = float(match.group('value'))
                    traits[name] = value
            else:
                break
        multiplier = MassObject(mass=1.0, cg=numpy.ones(3), inertia_moment=numpy.ones(3), cross_inertia=numpy.ones(3))
        adder = MassObject(mass=0.0, cg=numpy.zeros(3), inertia_moment=numpy.zeros(3), cross_inertia=numpy.zeros(3))
        traits['objects'] = []
        for line in lines[i:]:
            vals = [float(num) for num in line.split()]
            cross_inertia = numpy.zeros(3)
            if len(vals) > 7:
                cross_inertia[:] = vals[7:]
            mass=vals[0]
            cg=vals[1:4]
            inertia_moment=vals[4:7]
            massobj = MassObject(mass=multiplier.mass*mass+adder.mass,
                                 cg=multiplier.cg * cg + adder.cg,
                                 inertia_moment=multiplier.inertia_moment * inertia_moment + adder.inertia_moment,
                                 cross_inertia=multiplier.cross_inertia * cross_inertia + adder.cross_inertia,
                                 )
            traits['objects'].append(massobj)
        return Mass(**traits)
