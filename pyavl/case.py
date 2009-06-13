'''
Created on Jun 8, 2009

@author: pankaj
'''

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


class Case(object):
    '''
    A class representing an avl input file
    '''
    
    def __init__(self, casename, mach_no, symmetry, ref_area, ref_chord, ref_span, ref_cg, CD_p=None, geometry=None):
        '''
        Constructor
        '''
        self.casename = casename
        self.mach_no = mach_no
        self.symmetry = symmetry
        self.ref_area = ref_area
        self.ref_chord = ref_chord
        self.ref_span = ref_span
        self.ref_cg = ref_cg
        self.CD_p = CD_p
        self.geometry = geometry
    
    def write_input_file(self, file):
        '''
        Write all the data in the case in the appropriate format as in input .avl file for the AVL program
        '''
        file.write(self.casename + '\n')
        file.write('#Mach no\n%f\n' % self.mach_no)
        file.write('#iYsym\tiZsym\tZsym\n%d\t%d\t%f\n' % tuple(self.symmetry))
        file.write('#Sref\tCref\tBref\n%f\t%f\t%f\n' % (self.ref_area, self.ref_chord, self.ref_span))
        file.write('#Xref\tYref\tZref\n%f\t%f\t%f\n' % tuple(self.ref_cg))
        if self.CD_p is not None:
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
        mach_no = float(lines[1])
        symmetry = lines[2].split()
        symmetry = [int(symmetry[0]), int(symmetry[1]), float(symmetry[2])]
        ref_area, ref_chord, ref_span = [float(value) for value in lines[3].split()]
        ref_cg = [float(value) for value in lines[4].split()]
        lineno = 5
        try:
            CD_p = float(lines[5])
            lineno = 6
        except ValueError:
            CD_p = None
        geometry = Geometry.create_from_lines(lines, lineno)
        case = Case(casename, mach_no, symmetry, ref_area, ref_chord, ref_span, ref_cg, CD_p, geometry)
        return case