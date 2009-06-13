'''
Created on Jun 9, 2009

@author: pankaj
'''

def is_sequence(object):
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

class Geometry(object):
    '''
    A class representing the geometry for a case in avl
    '''
    def __init__(self):
        self.surfaces = {}
        self.bodies = {}
    
    def write_to_file(self, file):
        file.write('# SURFACES\n')
        for surfacename, surface in self.surfaces.iteritems():
            surface.write_to_file(file)
            file.write('\n')
        file.write('# END SURFACES\n\n')
        file.write('# BODIES\n')
        for bodyname, body in self.bodies.iteritems():
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
                geometry.surfaces[surface.name] = surface
            elif 'BODY' == lines[lineno].upper():
                body, lineno = Body.create_from_lines(lines, lineno)
                geometry.bodies[bodies.name] = body
        return geometry
    
class Surface(object):
    '''
    Class representing a surface in AVL geometry
    '''
    def __init__(self, name, cvortices, svortices=None, index=None, yduplicate=None, scale=None, translate=None, angle=None):
        '''
        cvortices, svortices = (number of vortices, spacing parameter) for chordwise, spanwise vortex distribution
        '''
        self.name = name
        self.cvortices = cvortices
        self.svortices = svortices
        self.index = index
        self.yduplicate = yduplicate
        self.scale = scale
        self.translate = translate
        self.angle = angle
        self.sections = []
    
    def write_to_file(self, file):
        file.write('SURFACE\n')
        file.write(self.name)
        file.write('\n')
        file.write('# Nchord\tCspace\t[ Nspan\tSspace ]\n')
        file.write('%d\t%f' % tuple(self.cvortices))
        if self.svortices is not None: file.write('\t%d\t%f' % tuple(self.svortices))
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
        surface = Surface(name, cvortices, svortices)
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
    

class Control(object):
    def __init__(self, name, gain, x_hinge, hinge_vec, sign_dup):
        self.name = name
        self.gain = gain
        self.x_hinge = x_hinge
        self.hinge_vec = hinge_vec
        self.sign_dup = sign_dup
    
    def write_to_file(self, file):
        file.write('CONTROL\n')
        file.write('#Cname   Cgain  Xhinge  HingeVec      SgnDup\n')
        file.write('%s\t%f\t%f\t' % (self.name, self.gain, self.x_hinge))
        file.write('%f %f %f\t' % tuple(self.hinge_vec))
        file.write('%f\n' % self.sign_dup)
        file.write('')

class DesignParameter(object):
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
    
    def write_to_file(self, file):
        file.write('DESIGN\n%s\t%f\n' % (self.name, self.weight))
        
class Section(object):
    '''
    Class representing a section of a section (flat plate)
    '''
    def __init__(self, leading_edge, chord, angle, svortices=None):
        '''
        Xle Yle Zle Chord Ainc [ Nspan Sspace ]
        CLAF and CDCL if required to be set must be set after initiation
        '''
        self.leading_edge = leading_edge
        self.chord = chord
        self.angle = angle
        self.svortices = svortices
        self.claf = None
        self.cd_cl = None
        self.controls = {}
        self.design_params = {}
    
    def write_to_file(self, file, write_section=3):
        '''write_section = sum of section to write
        header section (SECTION+DATAline) = 1
        other data section = 2
        therefore 3 => write complete section
        this argument is important only for the subclasses to insert camberline data between the two sections
        '''
        # TODO: implement
        if (write_section // 1) % 2 == 1:
            file.write('SECTION\n')
            file.write('#Xle   Yle   Zle   Chord  Ainc  [ Nspan Sspace ]\n')
            file.write('%f\t%f\t%f' % tuple(self.leading_edge))
            file.write('\t%f\t%f' % (self.chord, self.angle))
            if self.svortices is not None: file.write('\t%d\t%f' % tuple(self.svortices))
            file.write('\n')
        if (write_section // 2) % 2 == 1:
            if self.cd_cl is not None:
                file.write('CDCL\n')
                for point in self.cd_cl:
                    file.write('%f\t%f\n' % point)
            if self.claf is not None: file.write('CLAF\n%f\n' % self.claf)
            for design_param in self.design_params.itervalues(): design_param.write_to_file(file)
            for control in self.controls.itervalues(): control.write_to_file(file)
        file.write('')
        file.write('')
    
    @classmethod
    def create_from_lines(cls, lines, lineno):
        #TODO:
        data = [float(val) for val in lines[lineno + 1].split()]
        leading_edge = data[:3]
        chord = data[3]
        angle = data[4]
        if len(data) == 7:
            svortices = data[5:]
        else:
            svortices = None
        lineno += 2
        
        if lines[lineno].startswith('NACA'):
            number = int(lines[lineno + 1])
            section = SectionNACA(leading_edge, chord, angle, number, svortices)
            lineno += 2
            
        elif lines[lineno].startswith('AIRFOIL'):
            x_range = lines[lineno + 1].split()
            if len(range) == 3:
                x_range = [float(val) for val in range[1:]]
            else:
                x_range = None
            lineno += 1
            data = []
            while lineno < numlines:
                datapt = lines[lineno].split()
                if len(datapt) != 2:
                    break
                datapt = [float(val) for val in datapt]
                data.append(datapt)
                lineno += 1
                datapt = lines[lineno].split()
            section = SectionAIRFOIL(leading_edge, chord, angle, data, x_range, svortices)
            
        elif lines[lineno].startswith('AFILE'):
            x_range = lines[lineno + 1].split()
            if len(x_range) == 3:
                x_range = [float(val) for val in range[1:]]
            else:
                x_range = None
            filename = lines[lineno + 1]
            section = SectionAFILE(leading_edge, chord, angle, filename, x_range, svortices)
            lineno += 2
            
        else: # flat plate airfoil section
            section = Section(leading_edge, chord, angle, svortices)
        
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
        
class SectionAFILE(Section):
    '''
    Class representing a section defined by an external file
    '''
    def __init__(self, leading_edge, chord, angle, filename, x_range=None, svortices=None):
        Section.__init__(self, leading_edge, chord, angle, svortices)
        self.filename = filename
        self.x_range = x_range
    
    def write_to_file(self, file):
        Section.write_to_file(self, file, 1)
        file.write('AFILE')
        if self.x_range is not None: file.write('\t%f\t%f' % self.x_range)
        file.write('\n%s\n' % self.filename)
        Section.write_to_file(self, file, 2)
    

class SectionAIRFOIL(Section):
    '''
    Class representing a section defined by airfoil data
    '''
    def __init__(self, leading_edge, chord, angle, data, x_range=None, svortices=None):
        Section.__init__(self, leading_edge, chord, angle, svortices)
        self.data = data
        self.x_range = x_range
    
    def write_to_file(self, file):
        Section.write_to_file(self, file, 1)
        file.write('AIRFOIL')
        if self.x_range is not None: file.write('\t%f\t%f' % self.x_range)
        file.write('\n')
        for point in self.data: file.write('%f\t%f\n' % point)
        file.write('\n')
        Section.write_to_file(self, file, 2)
    
        
class SectionNACA(Section):
    '''
    Class representing a section defined by airfoil data
    '''
    def __init__(self, leading_edge, chord, angle, number, svortices=None):
        Section.__init__(self, leading_edge, chord, angle, svortices)
        self.number = number
    
    def write_to_file(self, file):
        Section.write_to_file(self, file, 1)
        file.write('NACA\n%d\n' % self.number)
        Section.write_to_file(self, file, 2)

class Body(object):
    '''
    Class representing a body modeled by source-sink doublet
    '''
    def __init__(self, name, lsources, filename, yduplicate=None, scale=None, translate=None):
        self.name = name
        self.lsources = lsources
        self.filename = filename
        self.yduplicate = yduplicate
        self.scale = scale
        self.translate = translate
    
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
        name = lines[lineno+1]
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