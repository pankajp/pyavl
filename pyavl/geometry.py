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
                for i in attr: file.write('%s\t' %str(i))
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
        # TODO: implement
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
    def geometry_from_lines(self, lines, lineno):
        '''
        creates a geometry object from the lines representing the geometry in an avl input file
        lines are filtered lines and lineno is the line number where the geometry section starts (generally line no 6 or 7)
        returns a tuple of the geometry and the line number till which geometry input existed (generally the last line)
        '''
        
    
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
        file.write('%d\t%f' % self.cvortices)
        if self.svortices is not None: file.write('%d\t%f' % self.svortices)
        file.write('\n')
        write_vars(['index', 'yduplicate', 'scale', 'translate', 'angle'], self, file)
        for section in self.sections:
            section.write_to_file(file)
            file.write('\n')

class Control(object):
    def __init__(self, name, gain, x_hinge, hinge_vec, sign_dup):
        self.name = name
        self.gain = gain
        self.x_hinge = x_hinge
        self.hinge_vec = hinge_vec
        self.sign_dup = sign_dup
    
    def write_to_file(self, file):
        file.write('CONTROL\n')
        file.write('%s\t%f\t%f\t%f\t' % (self.name, self.gain, self.x_hinge))
        file.write('%f %f %f\t' % self.hinge_vec)
        file.write('%d\n' % self.sign_dup)
        file.write('')

class DesignParameter(object):
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
    
    def write_to_file(self, file):
        file.write('DESIGN\n%s\t%f\n' % (self.name, self.weight))
        
class Section(object):
    '''
    Class representing a section of a surface
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
    
    def write_to_file(self, file):
        # TODO: implement
        file.write('SECTION\n')
        file.write('Xle Yle Zle Chord Ainc [ Nspan Sspace ]\n')
        file.write('%f\t%f\t%f' % self.leading_edge)
        file.write('\t%f\t%f' % (self.chord, self.angle))
        if self.svortices is not None: file.write('\t%d\t%f' % self.svortices)
        file.write('\n')
        if self.cd_cl is not None:
            file.write('CDCL\n')
            for point in self.cd_cl:
                file.write('%f\t%f\n' %point)
        if self.claf is not None: file.write('CLAF\n%f\n' %self.claf)
        for design_param in self.design_params.itervalues(): design_param.write_to_file(file)
        for control in self.controls.itervalues(): control.write_to_file(file)
        file.write('')
        file.write('')

class SectionAFILE(Section):
    '''
    Class representing a section defined by an external file
    '''
    def __init__(self, leading_edge, chord, angle, filename, x_range=None, svortices=None):
        super.__init__(self, leading_edge, chord, angle, svortices)
        self.filename = filename
        self.x_range = x_range
    
    def write_to_file(self, file):
        Section.write_to_file(self, file)
        file.write('AFILE')
        if self.x_range is not None: file.write('\t%f\t%f' % self.x_range)
        file.write('\n%s\n' % self.filename)
        

class SectionAIRFOIL(Section):
    '''
    Class representing a section defined by airfoil data
    '''
    def __init__(self, leading_edge, chord, angle, data, x_range=None, svortices=None):
        super.__init__(self, leading_edge, chord, angle, svortices)
        self.data = data
        self.x_range = x_range
    
    def write_to_file(self, file):
        Section.write_to_file(self, file)
        file.write('AIRFOIL')
        if self.x_range is not None: file.write('\t%f\t%f' % self.x_range)
        file.write('\n')
        for point in self.data: file.write('%f\t%f\n' % point)
        file.write('\n')
        
class SectionNACA(Section):
    '''
    Class representing a section defined by airfoil data
    '''
    def __init__(self, leading_edge, chord, angle, number, svortices=None):
        super.__init__(self, leading_edge, chord, angle, svortices)
        self.number = number
    
    def write_to_file(self, file):
        Section.write_to_file(self, file)
        file.write('NACA\n%d\n' % self.number)

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
        file.write('%s\n' %self.name)
        write_vars(['yduplicate', 'scale', 'translate'], self, file)
        file.write('BFILE\n')
        file.write('%s\n' %self.filename)
        file.write('')
        file.write('')
        file.write('')
