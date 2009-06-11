'''
Created on Jun 8, 2009

@author: pankaj
'''

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
        file.write(self.casename+'\n')
        file.write('#Mach no\n%f\n' %self.mach_no)
        file.write('#iYsym\tiZsym\tZsym\n%d\t%d\t%f\n' % self.symmetry)
        file.write('#Sref\tCref\tBref\n%f\t%f\t%f\n' %(self.ref_area, self.ref_chord, self.ref_span))
        file.write('#Xref\tYref\tZref\n%f\t%f\t%f\n' % self.ref_cg)
        if self.CD_p is not None:
            file.write('#CD_p profile drag coefficient\n%f\n' % self.CD_p)
        file.write('\n')
        file.write('#'*70)
        file.write('\n')
        self.geometry.write_to_file(file)
        file.write('')        