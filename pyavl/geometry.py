'''
Created on Jun 9, 2009

@author: pankaj
'''
import os
import numpy

from pyavl.utils.naca4_plotter import get_NACA4_data
from pyavl.utils.numerical import false_position_method

from enthought.traits.api import HasTraits, List, Str, Float, Range, Int, Dict, Button, \
        File, Trait, Instance, Enum, Array, cached_property, Property, String, Directory, \
        on_trait_change
from enthought.traits.ui.api import View, Item, Group, ListEditor, ArrayEditor, ListStrEditor, \
    HGroup
from enthought.traits.ui.value_tree import TraitsNode

def is_sequence(obj):
     try:
         test = obj[0:0]
     except:
         return False
     else:
         return True

def write_vars(vars, obj, file):
    for var in vars:
        attr = getattr(obj, var, None)
        #attr = obj.__dict__.get(var,None)
        if attr is not None:
            if is_sequence(attr):
                file.write('%s\n' % (var.upper()))
                for i in attr: file.write('%s    ' % str(i))
            else:
                file.write('%s\n%s' % (var.upper(), str(attr)))
            file.write('\n')

class Control(HasTraits):
    name = Str('Unnamed control surface')
    gain = Float
    x_hinge = Float
    hinge_vec = Array(numpy.float, (3,))
    sign_dup = Float
    
    def write_to_file(self, file):
        file.write('CONTROL\n')
        file.write('#Cname   Cgain  Xhinge  HingeVec      SgnDup\n')
        file.write('%s    %f    %f    ' % (self.name, self.gain, self.x_hinge))
        file.write('%f %f %f    ' % tuple(self.hinge_vec))
        file.write('%f\n' % self.sign_dup)
        file.write('')

class DesignParameter(HasTraits):
    name = Str('Unnamed Design Parameter')
    weight = Float
    
    def write_to_file(self, file):
        file.write('DESIGN\n%s    %f\n' % (self.name, self.weight))

class SectionData(HasTraits):
    type = 'flat plate'
    def write_to_file(self, file):
        pass        
    
    def write_airfoil_file(self, filename, name='airfoil'):
        file = open(filename,'w')
        data_points = self.get_data_points()
        for row in data_points:
            file.write('%f    %f\n' %(row[0],row[1]))
        file.close()
    
    data_points = Array(numpy.float, ((2, None), 2), numpy.array([[0.0, 0.0],
                                                                  [1.0, 0.0]]))
    traits_view = View()
    def get_data_points(self):
        return numpy.array([[0.0, 0.0],
                      [1.0, 0.0]])

class SectionAFILEData(SectionData):
    type = 'airfoil data file'
    filename = File
    x_range = List(Float, [0.0, 1.0], 2, 2)
    cwd = Directory('')
    data_points = Property(Array(numpy.float, ((2, None), 2), numpy.array([[0., 0.], [1., 0.]])), depends_on='filename')
    traits_view = View(['filename', 'cwd', 'x_range'])
    @cached_property
    def _get_data_points(self):
        try:
            return numpy.loadtxt(open(os.path.join(self.cwd, self.filename)), skiprows=1)
        except:
            return numpy.array([[0., 0.], [1., 0.]])
    
    def write_to_file(self, file):
        file.write('AFILE')
        if self.x_range != [0.0, 1.0]: file.write('    %f    %f' % tuple(self.x_range))
        file.write('\n%s\n' % self.filename)
    
    def get_data_points(self):
        return self.data_points

class SectionAIRFOILData(SectionData):
    type = 'airfoil data'
    data_points = Array(numpy.float, ((2, None), 2), numpy.array([[0., 0.], [1., 0.]]))
    x_range = List(Float, [0.0, 1.0], 2, 2)
    traits_view = View(['data_points', 'x_range'])
    def write_to_file(self, file):
        file.write('AIRFOIL')
        if self.x_range != [0.0, 1.0]: file.write('    %f    %f' % self.x_range)
        file.write('\n')
        for point in self.data_points: file.write('%f    %f\n' %(point[0],point[1]))
        file.write('\n')
    
    def get_data_points(self):
        return self.data_points
    
    @classmethod
    def get_clipped_section(cls, section, inlet_height, angle):
        sectiondata = cls.get_clipped_section_data(section.data, inlet_height, angle)
        ret = Section(type=sectiondata.type)
        ret.chord = section.chord
        ret.angle = section.angle
        ret.svortices = section.svortices
        ret.claf = section.claf
        ret.cd_cl = section.cd_cl
        ret.controls = section.controls
        ret.design_params = section.design_params
        ret.cwd = section.cwd
        ret.data = sectiondata
        ret.leading_egde = section.leading_egde
        return ret
    
    @classmethod
    def get_clipped_section_data(cls, sectiondata, inlet_height, angle):
        '''Function to get a SectionAIRFOILData instance from a SectionData as 
        required for a parafoil by clipping the front portion as specified by
        the inlet height and angle of cut
        '''
        dx = sectiondata.data_points[:, 0]
        xmin, xmax = numpy.min(dx), numpy.max(dx)
        xchange = numpy.argmax(dx) if dx[1] > dx[0] else numpy.argmin(dx)
        x = numpy.unique(dx)
        
        # datax, datay
        dxu, dyu = sectiondata.data_points[:xchange+1, 0], sectiondata.data_points[:xchange+1, 1]
        a = numpy.argsort(dxu)
        dxu, dyu = dxu[a], dyu[a]
        dxl, dyl = sectiondata.data_points[xchange:, 0], sectiondata.data_points[xchange:, 1]
        a = numpy.argsort(dxl)
        dxl, dyl = dxl[a], dyl[a]
        
        angle_r = angle * numpy.pi / 180
        #def err_angle
        err_angle = lambda x,x1,y1: angle_r - numpy.arctan2(y1 - numpy.interp(x, dxl, dyl), x1 - x)
        get_err_angle = lambda x1,y1: lambda x: err_angle(x,x1,y1)
        def get_inlet_height(x, angle):
            x1 = x
            y1 = numpy.interp(x1, dxu, dxu)
            x2 = false_position_method(get_err_angle(x1,y1), x1, x1 + 0.01, angle_r / 100, max_iter=100)
            y2 = numpy.interp(x, dxl, dyl)
            return y1 - y2
        
        err_height = lambda x: get_inlet_height(x, angle) - inlet_height
        x1 = x_inlet = false_position_method(err_height, 0.1, 0.11, inlet_height / 1000, max_iter=100)[0]
        x2_inlet = false_position_method(get_err_angle(x1,numpy.interp(x1, dxu, dxu)), x1, x1 + 0.01, angle_r / 100, max_iter=100)[0]
        dxu_new = dxu[dxu>x_inlet]
        dxu_new = numpy.concatenate(([x_inlet],dxu_new))
        dyu_new = numpy.interp(dxu_new, dxu, dyu)
        dxl_new = dxl[dxl>x2_inlet]
        dxl_new = numpy.concatenate(([x2_inlet],dxl_new))
        dyl_new = numpy.interp(dxl_new, dxl, dyl)
        dx_new = numpy.concatenate((dxl_new[::-1],dxu_new))
        dy_new = numpy.concatenate((dyl_new[::-1],dyu_new))
        
        # now translate the data to get x_le = 0.0
        dx_new = dx_new-x_inlet
        # now scale to get initial chord to compensate for the cut
        dx_new = dx_new/(1-x_inlet)
        dy_new = dy_new/(1-x_inlet)
        data_points = numpy.array([dx_new,dy_new]).T
        print data_points.shape
        ret = SectionAIRFOILData(data_points=data_points)
        return ret
    
class SectionNACAData(SectionData):
    type = 'NACA'
    number = Int
    data_points = Property(Array(numpy.float, ((2, None), 2), numpy.array([[0., 0.], [1., 0.]])), depends_on='number')
    traits_view = View(['number'])
    @cached_property
    def _get_data_points(self):
        return get_NACA4_data(self.number)
    
    def write_to_file(self, file):
        file.write('NACA\n%d\n' % self.number)
    
    def get_data_points(self):
        return self.data_points

class Section(HasTraits):
    '''
    Class representing a section of a surface (flat plate)
    '''
    leading_edge = Array(numpy.float, (3,))
    chord = Float(1)
    angle = Float
    svortices = List(value=[10, 1.0], minlen=2, maxlen=2)
    claf = Float(1.0)
    cd_cl = Array(numpy.float, (3, 2))
    controls = List(Control, [])
    design_params = Dict(String, Instance(DesignParameter), {})
    type = Enum('flat plate', 'airfoil data', 'airfoil data file', 'NACA')
    data = Instance(SectionData, SectionData())
    cwd = Directory
    delete_section = Button()
    
    def _type_changed(self):
        if self.type == 'flat plate':
            self.data = SectionData()
        elif self.type == 'airfoil data':
            self.data = SectionAIRFOILData()
        elif self.type == 'airfoil data file':
            self.data = SectionAFILEData()
        elif self.type == 'NACA':
            self.data = SectionNACAData()
    
    traits_view = View(Item('leading_edge', editor=ArrayEditor()),
                       Item('chord'),
                       Item('angle'),
                       Item('svortices'),
                       Item('claf'),
                       Item('cd_cl', editor=ArrayEditor()),
                       Item('design_params'),
                       Item('type'),
                       Item('data', style='custom'),
                       Item('delete_section', show_label=False),
                       )
    
    
    def write_to_file(self, file):
        # TODO: implement
        file.write('SECTION\n')
        file.write('#Xle   Yle   Zle   Chord  Ainc  [ Nspan Sspace ]\n')
        file.write('%f    %f    %f' % tuple(self.leading_edge))
        file.write('    %f    %f' % (self.chord, self.angle))
        file.write('    %d    %f' % tuple(self.svortices))
        file.write('\n')
        self.data.write_to_file(file)
        if numpy.any(numpy.isnan(self.cd_cl)):
            file.write('CDCL\n')
            for point in self.cd_cl:
                file.write('%f    %f\n' % point)
        if self.claf != 0.0: file.write('CLAF\n%f\n' % self.claf)
        for design_param in self.design_params: design_param.write_to_file(file)
        for control in self.controls: control.write_to_file(file)
        file.write('')
    
    @classmethod
    def create_from_lines(cls, lines, lineno, cwd=cwd):
        #TODO:
        dataline = [float(val) for val in lines[lineno + 1].split()]
        leading_edge = dataline[:3]
        chord = dataline[3]
        angle = dataline[4]
        if len(dataline) == 7:
            svortices = dataline[5:]
        else:
            svortices = [0, 1.0]
        lineno += 2
        section = Section(leading_edge=leading_edge, chord=chord, angle=angle, svortices=svortices)
        numlines = len(lines)
        if lineno >= numlines:
            section.data = SectionData()
        elif lines[lineno].startswith('NACA'):
            number = int(lines[lineno + 1])
            section.type = 'NACA'
            section.data = SectionNACAData(number=number)
            lineno += 2
        elif lines[lineno].startswith('AIRF'):
            x_range = lines[lineno + 1].split()
            if len(x_range) == 3:
                x_range = [float(val) for val in range[1:]]
            else:
                x_range = [0.0,1.0]
            lineno += 1
            dataline = []
            while lineno < numlines:
                datapt = lines[lineno].split()
                if len(datapt) != 2:
                    break
                datapt = [float(val) for val in datapt]
                dataline.append(datapt)
                lineno += 1
                datapt = lines[lineno].split()
            section.type = 'airfoil data'
            section.data = SectionAIRFOILData(x_range=x_range, data=dataline)
        elif lines[lineno].startswith('AFIL'):
            x_range = lines[lineno + 1].split()
            if len(x_range) == 3:
                x_range = [float(val) for val in range[1:]]
            else:
                x_range = [0.0, 1.0]
            filename = lines[lineno + 1]
            section.type = 'airfoil data file'
            section.data = SectionAFILEData(x_range=x_range, filename=filename, cwd=cwd)
            lineno += 2
        else:
            section.data = SectionData()
        
        while lineno < numlines:
            cmd = lines[lineno]
            if cmd.startswith('CLAF'):
                section.claf = float(lines[lineno + 1])
                lineno += 2
            elif cmd.startswith('CDCL'):
                section.cd_cl = float(lines[lineno + 1])
                lineno += 2
            elif cmd.startswith('CONT'):
                cdata = lines[lineno + 1].split()
                name = cdata[0]
                cdata = [float(val) for val in cdata[1:]]
                gain, x_hinge = cdata[:2]
                hinge_vec = cdata[2:5]
                sign_dup = cdata[5]
                control = Control(name=name, gain=gain, x_hinge=x_hinge, hinge_vec=hinge_vec, sign_dup=sign_dup)
                section.controls.append(control)
                lineno += 2
            elif cmd.startswith('CLAF'):
                section.claf = float(lines[lineno + 1])
                lineno += 2
            elif cmd.startswith('DESI'):
                ddata = lines[lineno + 1].split()
                name = ddata[0]
                weight = float(ddata[1])
                design = DesignParameter(name=name, weight=weight)
                section.design_params[name] = design
                lineno += 2
            else:
                break
        return section, lineno
        

class Body(HasTraits):
    '''
    Class representing a body modeled by source-sink doublet
    '''
    name = Str('Unnamed Body')
    lsources = List(value=[8, 1], minlen=2, maxlen=2)
    filename = File
    yduplicate = Float(numpy.nan)
    scale = Array(numpy.float, (3,), numpy.ones((3,)))
    translate = Array(numpy.float, (3,))
    num_pts = Int(10)
    delete_body = Button()
    # pt, xy
    data = Property(Array(numpy.float), depends_on='filename')
    cwd = Directory
    @cached_property
    def _get_data(self):
        return numpy.loadtxt(open(os.path.join(self.cwd, self.filename)), skiprows=1)
    
    traits_view = View(Item('name'),
                       Item('lsources'),
                       Item('filename'),
                       Item('cwd'),
                       Item('yduplicate'),
                       Item('scale', editor=ArrayEditor()),
                       Item('translate', editor=ArrayEditor()),
                       Item('num_pts'),
                       Item('delete_body', show_label=False),
                       )
    
    def write_to_file(self, file):
        file.write('BODY\n')
        file.write('%s\n' % self.name)
        if numpy.isfinite(self.yduplicate):
            write_vars(['yduplicate'], self, file)
        write_vars(['scale', 'translate'], self, file)
        file.write('BFILE\n')
        file.write('%s\n' % self.filename)
        file.write('')
        file.write('')
        file.write('')
    
    @classmethod
    def create_from_lines(cls, lines, lineno, cwd=cwd):
        name = lines[lineno + 1]
        sources = lines[lineno + 2].split()
        lsources = [int(sources[0]), float(sources[1])]
        body = Body(name=name, lsources=lsources, cwd=cwd)
        lineno += 3
        numlines = len(lines)
        while lineno < numlines:
            cmd = lines[lineno]
            if cmd.startswith('YDUP'):
                yduplicate = float(lines[lineno + 1])
                body.yduplicate = yduplicate
                lineno += 2
            elif cmd.startswith('SCAL'):
                scale = [float(val) for val in lines[lineno + 1].split()]
                body.scale = scale
                lineno += 2
            elif cmd.startswith('TRAN'):
                translate = [float(val) for val in lines[lineno + 1].split()]
                body.translate = translate
                lineno += 2
            elif cmd.startswith('BFIL'):
                filename = lines[lineno + 1]
                body.filename = filename
                lineno += 2
            else:
                break
        return body, lineno


class Surface(HasTraits):
    '''
    Class representing a surface in AVL geometry
    '''
    
    name = Str('Unnamed surface')
    cvortices = List(value=[8, 1], minlen=2, maxlen=2)
    svortices = List(value=[0, 1.0], minlen=2, maxlen=2)
    index = Int
    yduplicate = Float(numpy.nan)
    scale = Array(numpy.float, (3,), numpy.ones((3,)))
    translate = Array(numpy.float, (3,))
    angle = Float
    sections = List(Section, [])
    cwd = Directory
    add_section = Button()
    delete_surface = Button()
    
    traits_view = View(Item('name'),
                       Item('cvortices'),
                       Item('svortices'),
                       Item('index'),
                       Item('yduplicate'),
                       Item('scale', editor=ArrayEditor()),
                       Item('translate', editor=ArrayEditor()),
                       Item('angle'),
                       HGroup(Item('add_section'), Item('delete_surface'), show_labels=False),
                       )
    
    @on_trait_change('sections.delete_section')
    def delete_section(self, object, name, new):
        if name == 'delete_section':
            self.sections.remove(object)
    
    def write_to_file(self, file):
        file.write('SURFACE\n')
        file.write(self.name)
        file.write('\n')
        file.write('# Nchord    Cspace    [ Nspan    Sspace ]\n')
        file.write('%s    %s' % tuple(self.cvortices))
        if self.svortices[0] != 0: file.write('    %d    %f' % (self.svortices[0], self.svortices[1]))
        file.write('\n')
        if numpy.isfinite(self.yduplicate):
            write_vars(['yduplicate'], self, file)
        write_vars(['index', 'scale', 'translate', 'angle'], self, file)
        for section in self.sections:
            section.write_to_file(file)
            file.write('\n')
    
    @classmethod
    def create_from_lines(cls, lines, lineno, cwd=cwd):
        # assert lines[lineno] == 'SURFACE'
        name = lines[lineno + 1]
        vortices = lines[lineno + 2].split()
        cvortices = [int(vortices[0]), float(vortices[1])]
        if len(vortices) == 4:
            svortices = [int(vortices[2]), float(vortices[3])]
        else:
            svortices = [0, 1.0]
        surface = Surface(name=name, cvortices=cvortices, svortices=svortices, cwd=cwd)
        lineno += 3
        numlines = len(lines)
        while lineno < numlines:
            cmd = lines[lineno]
            if cmd.startswith('INDE'):
                surface.index = int(lines[lineno + 1])
                lineno += 2
            elif cmd.startswith('YDUP'):
                surface.yduplicate = float(lines[lineno + 1])
                lineno += 2
            elif cmd.startswith('SCAL'):
                surface.scale = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            elif cmd.startswith('TRAN'):
                surface.translate = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            elif cmd.startswith('ANGL'):
                surface.angle = float(lines[lineno + 1])
                lineno += 2
            elif cmd.startswith('SECT'):
                section, lineno = Section.create_from_lines(lines, lineno, cwd=cwd)
                surface.sections.append(section)
            else:
                break
        return surface, lineno


class Geometry(TraitsNode):
    '''
    A class representing the geometry for a case in avl
    '''
    
    surfaces = List(Surface, [])
    bodies = List(Body, [])
    controls = Property(List(String), depends_on='surfaces')
    cwd = Directory
    add_surface = Button()
    add_body = Button()
    add_parafoil = Button()
    refresh_geometry_view = Button()
    traits_view = View(HGroup(Item('add_surface'), Item('add_parafoil'), Item('add_body'), Item('refresh_geometry_view'), show_labels=False),
                       Item('controls', editor=ListStrEditor(editable=False, operations=[]), style='readonly')
                       )
    def _add_surface_fired(self):
        surface = Surface(sections=[Section(), Section(leading_edge=numpy.array([0, 1, 0]), yduplicate=0)])
        self.surfaces.append(surface)
        self.refresh_geometry_view = True
    
    def _add_body_fired(self):
        body = Body()
        self.bodies.append(body)
        self.refresh_geometry_view = True
    
    def _add_parafoil_fired(self):
        from pyavl.utils.wizards.parafoil import ParafoilWizard
        pw = ParafoilWizard()
        if pw.edit_traits(kind='livemodal'):
            self.surfaces.append(pw.get_surface())
        self.refresh_geometry_view = True
    
    @on_trait_change('bodies.delete_body,surfaces.delete_surface, surfaces.sections.delete_section')
    def delete_part(self, object, name, new):
        if name == 'delete_surface':
            self.surfaces.remove(object)
        elif name == 'delete_body':
            self.bodies.remove(object)
        self.refresh_geometry_view = True
    
    @cached_property
    def _get_controls(self):
        ret = set([])
        for surface in self.surfaces:
            for section in surface.sections:
                for control in section.controls:
                    ret.add(control.name)
        return list(ret)
        
    
    def write_to_file(self, file):
        file.write('# SURFACES\n')
        for surface in self.surfaces:
            surface.write_to_file(file)
            file.write('\n')
        file.write('# END SURFACES\n\n')
        file.write('# BODIES\n')
        for body in self.bodies:
            body.write_to_file(file)
            file.write('\n')
        file.write('# END BODIES\n\n')
    
    @classmethod
    def create_from_lines(cls, lines, lineno, cwd=''):
        '''
        creates a geometry object from the lines representing the geometry in an avl input file
        lines are filtered lines and lineno is the line number where the geometry section starts (generally line no 6 or 7)
        returns a tuple of the geometry and the line number till which geometry input existed (generally the last line)
        '''
        numlines = len(lines)
        geometry = Geometry(cwd=cwd)
        while lineno < numlines:
            if lines[lineno].upper().startswith('SURF'):
                surface, lineno = Surface.create_from_lines(lines, lineno, cwd=cwd)
                geometry.surfaces.append(surface)
            elif lines[lineno].upper().startswith('BODY'):
                body, lineno = Body.create_from_lines(lines, lineno, cwd=cwd)
                geometry.bodies.append(body)
            else:
                lineno += 1
        return geometry
