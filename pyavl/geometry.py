'''
Created on Jun 9, 2009

@author: pankaj
'''

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
        for surface in self.surfaces:
            surface.write_to_file(file)
            file.write('\n')
        file.write('# END SURFACES\n\n')
        file.write('# BODIES\n')
        for body in self.bodies:
            body.write_to_file(file)
            file.write('\n')
        file.write('# END BODIES\n\n')
        
    
class Surface(object):
    '''
    Class representing a surface in AVL geometry
    '''
    def __init__(self):
        self.sections = []
    
    def write_to_file(self, file):
        # TODO: implement
        for section in self.sections:
            section.write_to_file(file)
            file.write('\n')

class Control(object):
    pass

class Section(object):
    '''
    Class representing a section of a surface
    '''
    def __init__(self):
        self.controls = []
    
    def write_to_file(self, file):
        # TODO: implement
        pass

class SectionAFILE(Section):
    '''
    Class representing a section defined by an external file
    '''
    def __init__(self, filename):
        super.__init__(self)
        self.filename = filename

class SectionAIRFOIL(Section):
    '''
    Class representing a section defined by airfoil data
    '''
    def __init__(self, data):
        super.__init__(self)
        self.data = data
    
class SectionNACA(Section):
    '''
    Class representing a section defined by airfoil data
    '''
    def __init__(self, number):
        super.__init__(self)
        self.number = number
    

class Body(object):
    '''
    Class representing a body modeled by source-sink doublet
    '''
    def __init__(self, filename):
        self.filename = filename
