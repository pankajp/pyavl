'''
Created on Jun 9, 2009

@author: pankaj
'''

from enthought.traits.api import HasTraits, List, Str, Float, Range, Int, Dict, File, Trait, Instance, Enum, Array

Intn = Trait(None, None, Int)
Floatn = Trait(None, None, Float)
Vec = List(minlen=3, maxlen=3)
Vecn = Trait(None, None, Vec)

def is_sequence(obj):
     try:
         test = object[0:0]
     except:
         return False
     else:
         return True

def write_vars(vars, obj, file):
    for var in vars:
        attr = getattr(obj, var, None)
        if attr is not None:
            if is_sequence(attr):
                for i in attr: file.write('%s\t' % str(i))
            else:
                file.write('%s\n%s' % (var.upper(), str(attr)))
            file.write('\n')


class Control(HasTraits):
    name = Str('Unnamed control surface')
    gain = Float
    x_hinge = Float
    hinge_vec = Vec
    sign_dup = Float
    
    def write_to_file(self, file):
        file.write('CONTROL\n')
        file.write('#Cname   Cgain  Xhinge  HingeVec      SgnDup\n')
        file.write('%s\t%f\t%f\t' % (self.name, self.gain, self.x_hinge))
        file.write('%f %f %f\t' % tuple(self.hinge_vec))
        file.write('%f\n' % self.sign_dup)
        file.write('')

class DesignParameter(HasTraits):
    name = Str('Unnamed Design Parameter')
    weigt = Float
    
    def write_to_file(self, file):
        file.write('DESIGN\n%s\t%f\n' % (self.name, self.weight))

class SectionData(HasTraits):
    def write_to_file(self, file):
        pass

class SectionAFILEData(SectionData):
    filename = File
    x_range = Trait(None, None, List(Float, [0.0, 1.0], 2, 2))
    
    def write_to_file(self, file):
        file.write('AFILE')
        if self.x_range is not None: file.write('\t%f\t%f' % self.x_range)
        file.write('\n%s\n' % self.filename)

class SectionAIRFOILData(SectionData):
    data = Array
    x_range = Trait(None, None, List(Float, [0.0, 1.0], 2, 2))
    
    def write_to_file(self, file):
        file.write('AIRFOIL')
        if self.x_range is not None: file.write('\t%f\t%f' % self.x_range)
        file.write('\n')
        for point in self.data: file.write('%f\t%f\n' % point)
        file.write('\n')

class SectionNACAData(SectionData):
    number = Int
    
    def write_to_file(self, file):
        file.write('NACA\n%d\n' % self.number)
    

class Section(HasTraits):
    '''
    Class representing a section of a section (flat plate)
    '''
    leading_edge = Vec
    chord = Float
    angle = Float
    svortices = Trait(None, None, List)
    claf = Floatn
    cd_cl = Floatn
    controls = List(Instance(Control))
    design_params = List(Instance(DesignParameter))
    type = Enum('flat plate', 'airfoil data', 'airfoil data file', 'NACA')
    data = Instance(SectionData)
    
    def write_to_file(self, file):
        # TODO: implement
        file.write('SECTION\n')
        file.write('#Xle   Yle   Zle   Chord  Ainc  [ Nspan Sspace ]\n')
        file.write('%f\t%f\t%f' % tuple(self.leading_edge))
        file.write('\t%f\t%f' % (self.chord, self.angle))
        if self.svortices is not None: file.write('\t%d\t%f' % tuple(self.svortices))
        file.write('\n')
        self.data.write_to_file(file)
        if self.cd_cl is not None:
            file.write('CDCL\n')
            for point in self.cd_cl:
                file.write('%f\t%f\n' % point)
        if self.claf is not None: file.write('CLAF\n%f\n' % self.claf)
        for design_param in self.design_params: design_param.write_to_file(file)
        for control in self.controls: control.write_to_file(file)
        file.write('')
    
    @classmethod
    def create_from_lines(cls, lines, lineno):
        #TODO:
        dataline = [float(val) for val in lines[lineno + 1].split()]
        leading_edge = dataline[:3]
        chord = dataline[3]
        angle = dataline[4]
        if len(dataline) == 7:
            svortices = dataline[5:]
        else:
            svortices = None
        lineno += 2
        section = Section(leading_edge=leading_edge, chord=chord, angle=angle, svortices=svortices)
        
        if lines[lineno].startswith('NACA'):
            number = int(lines[lineno + 1])
            section.type = 'NACA'
            section.data = SectionNACAData(number=number)
            lineno += 2
        elif lines[lineno].startswith('AIRFOIL'):
            x_range = lines[lineno + 1].split()
            if len(range) == 3:
                x_range = [float(val) for val in range[1:]]
            else:
                x_range = None
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
        elif lines[lineno].startswith('AFILE'):
            x_range = lines[lineno + 1].split()
            if len(x_range) == 3:
                x_range = [float(val) for val in range[1:]]
            else:
                x_range = None
            filename = lines[lineno + 1]
            section.type = 'airfoil data file'
            section.data = SectionAFILEData(x_range=x_range, filename=filename)
            lineno += 2
        else:
            section.data = SectionData()
        
        numlines = len(lines)
        while lineno < numlines:
            cmd = lines[lineno]
            if cmd == 'CLAF':
                section.claf = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'CDCL':
                section.cd_cl = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'CONTROL':
                cdata = lines[lineno + 1].split()
                name = cdata[0]
                cdata = [float(val) for val in cdata[1:]]
                gain, x_hinge = cdata[:2]
                hinge_vec = cdata[2:5]
                sign_dup = cdata[5]
                control = Control(name, gain, x_hinge, hinge_vec, sign_dup)
                section.controls[name] = control
                lineno += 2
            elif cmd == 'DESIGN':
                section.claf = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'CLAF':
                ddata = lines[lineno + 1].split()
                name = ddata[0]
                weight = float(ddata[1])
                design = DesignParameter(name, weight)
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
    lsources = List
    filename = File
    yduplicate = Floatn
    scale = Vecn
    translate = Vecn
    
    def write_to_file(self, file):
        file.write('BODY\n')
        file.write('%s\n' % self.name)
        write_vars(['yduplicate', 'scale', 'translate'], self, file)
        file.write('BFILE\n')
        file.write('%s\n' % self.filename)
        file.write('')
        file.write('')
        file.write('')
    
    @classmethod
    def create_from_lines(cls, lines, lineno):
        name = lines[lineno + 1]
        sources = lines[lineno + 2].split()
        lsources = [int(sources[0]), float(sources[1])]
        surface = Surface(name, cvortices, svortices)
        yduplicate = None
        scale = None
        translate = None
        lineno += 3
        numlines = len(lines)
        while lineno < numlines:
            cmd = lines[lineno]
            if cmd == 'YDUPLICATE':
                yduplicate = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'SCALE':
                scale = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            elif cmd == 'TRANSLATE':
                translate = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            elif cmd == 'BFILE':
                filename = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            else:
                break
        body = Body(name, lsources, filename, yduplicate, scale, translate)
        return body, lineno


class Surface(HasTraits):
    '''
    Class representing a surface in AVL geometry
    '''
    
    name = Str('Unnamed surface')
    cvortices = List
    svortices = Trait(None, None,List)
    index = Intn
    yduplicate = Floatn
    scale = Vecn
    translate = Vecn
    angle = Floatn
    sections = List(Instance(Section))
        
    def write_to_file(self, file):
        file.write('SURFACE\n')
        file.write(self.name)
        file.write('\n')
        file.write('# Nchord\tCspace\t[ Nspan\tSspace ]\n')
        file.write('%d\t%f' % tuple(self.cvortices))
        if self.svortices is not None: file.write('\t%d\t%f' % self.svortices.num,self.svortices.distr)
        file.write('\n')
        write_vars(['index', 'yduplicate', 'scale', 'translate', 'angle'], self, file)
        for section in self.sections:
            section.write_to_file(file)
            file.write('\n')
    
    @classmethod
    def create_from_lines(cls, lines, lineno):
        # assert lines[lineno] == 'SURFACE'
        name = lines[lineno + 1]
        vortices = lines[lineno + 2].split()
        cvortices = [int(vortices[0]), float(vortices[1])]
        if len(vortices) == 4:
            svortices = [int(vortices[2]), float(vortices[3])]
        else:
            svortices = None
        surface = Surface(name=name, cvortices=cvortices, svortices=svortices)
        lineno += 3
        numlines = len(lines)
        while lineno < numlines:
            cmd = lines[lineno]
            if cmd == 'INDEX':
                surface.index = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'YDUPLICATE':
                surface.yduplicate = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'SCALE':
                surface.scale = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            elif cmd == 'TRANSLATE':
                surface.translate = [float(val) for val in lines[lineno + 1].split()]
                lineno += 2
            elif cmd == 'ANGLE':
                surface.angle = float(lines[lineno + 1])
                lineno += 2
            elif cmd == 'SECTION':
                section, lineno = Section.create_from_lines(lines, lineno)
                surface.sections.append(section)
            else:
                break
        return surface, lineno


class Geometry(HasTraits):
    '''
    A class representing the geometry for a case in avl
    '''
    
    surfaces = List(Instance(Surface))
    bodies = List(Instance(Body))
    
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
    def create_from_lines(cls, lines, lineno):
        '''
        creates a geometry object from the lines representing the geometry in an avl input file
        lines are filtered lines and lineno is the line number where the geometry section starts (generally line no 6 or 7)
        returns a tuple of the geometry and the line number till which geometry input existed (generally the last line)
        '''
        numlines = len(lines)
        geometry = Geometry()
        while lineno < numlines:
            if 'SURFACE' == lines[lineno].upper():
                surface, lineno = Surface.create_from_lines(lines, lineno)
                geometry.surfaces.append(surface)
            elif 'BODY' == lines[lineno].upper():
                body, lineno = Body.create_from_lines(lines, lineno)
                geometry.bodies.append(body)
        return geometry
